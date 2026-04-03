import copy
from typing import Any, Dict
from fastapi import HTTPException, Header
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, RetryCallState
from google.api_core.exceptions import (
    ServiceUnavailable,
    InternalServerError,
    DeadlineExceeded,
    BadGateway,
    ResourceExhausted,
)
import httpx
from byteplussdkarkruntime._exceptions import (
    ArkInternalServerError,
    ArkAPITimeoutError,
    ArkAPIConnectionError,
    ArkRateLimitError,
)
from openai import APIConnectionError, APITimeoutError, APIStatusError, RateLimitError
from config.logger import logger


async def verify_api_token(authorization: str = Header(...)):
    """Verify that the API token is provided."""
    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing API token")
    return token


def truncate_strings(obj: Any, max_len: int = 500) -> Any:
    """
    Recursively truncate strings longer than max_len in any nested structure.
    """
    if isinstance(obj, str):
        return obj[:max_len] + "..." if len(obj) > max_len else obj

    elif isinstance(obj, list):
        return [truncate_strings(item, max_len) for item in obj]

    elif isinstance(obj, dict):
        return {key: truncate_strings(value, max_len) for key, value in obj.items()}

    elif isinstance(obj, tuple):
        return tuple(truncate_strings(item, max_len) for item in obj)

    elif isinstance(obj, set):
        return {truncate_strings(item, max_len) for item in obj}

    return obj


GEMINI_NSFW_FINISH_REASONS = {
    "SAFETY",
    "RECITATION",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "SPII",
    "IMAGE_SAFETY",
    "IMAGE_PROHIBITED_CONTENT",
    "IMAGE_RECITATION",
    "NO_IMAGE",
}

GEMINI_RETRYABLE_FINISH_REASONS = {
    "MALFORMED_RESPONSE",
    "MISSING_THOUGHT_SIGNATURE",
    "TOO_MANY_TOOL_CALLS",
    "UNEXPECTED_TOOL_CALL",
    "MALFORMED_FUNCTION_CALL",
    "MAX_TOKENS",
    "LANGUAGE",
    "OTHER",
    "IMAGE_OTHER",
}


class GeminiRetryableFinishReasonError(Exception):
    """Raised when Gemini returns a retryable finish reason instead of images."""
    pass


def raise_or_return_nsfw_for_empty_gemini_response(response, image_response_cls):
    """
    Call this when a Gemini response contains no images.
    - NSFW finish reason  → returns ImageResponse(is_nsfw_detected=True)
    - Retryable / unknown → raises GeminiRetryableFinishReasonError to trigger retry
    """
    finish_reason = None
    if response.candidates:
        fr = response.candidates[0].finish_reason
        finish_reason = fr.name if fr is not None else None

    if finish_reason in GEMINI_NSFW_FINISH_REASONS:
        logger.warning(f"Gemini response blocked with NSFW finish reason: {finish_reason}")
        return image_response_cls(
            error=response.to_json_dict(),
            is_nsfw_detected=True,
            model_usage=response.usage_metadata,
        )

    logger.warning(f"Gemini response returned no images with retryable finish reason: {finish_reason}, retrying...")
    raise GeminiRetryableFinishReasonError(
        f"Gemini returned no images with finish_reason={finish_reason}"
    )


def _is_gemini_retryable(exc: BaseException) -> bool:
    """
    Returns True for errors that should be retried against the Gemini API.
    Handles:
    - Google API 503/500/502/504/429 transport errors (incl. ResourceExhausted)
    - SDK AttributeError bug: 503 responses with a string 'error' value cause
      AttributeError: 'str' object has no attribute 'get' in _api_client.py
    """
    if isinstance(exc, GeminiRetryableFinishReasonError):
        return True
    try:
        if isinstance(
            exc, (ServiceUnavailable, InternalServerError,
                  DeadlineExceeded, BadGateway, ResourceExhausted)
        ):
            return True
    except ImportError:
        pass
    if isinstance(exc, AttributeError) and "'str' object has no attribute 'get'" in str(
        exc
    ):
        return True
    error_message = str(exc)
    if (
        "503" in error_message
        or "429" in error_message
        or "overloaded" in error_message.lower()
        or "RESOURCE_EXHAUSTED" in error_message
        or "UNAVAILABLE" in error_message
    ):
        return True
    return False


_GEMINI_MAX_ATTEMPTS = 6


def _log_gemini_before_sleep(retry_state: RetryCallState) -> None:
    exc = retry_state.outcome.exception()
    wait = retry_state.next_action.sleep
    logger.warning(
        f"[Gemini Retry] Attempt {retry_state.attempt_number}/{_GEMINI_MAX_ATTEMPTS} failed | "
        f"{type(exc).__name__}: {exc} | "
        f"waiting {wait:.1f}s → attempt {retry_state.attempt_number + 1}"
    )


def _log_gemini_after(retry_state: RetryCallState) -> None:
    if retry_state.attempt_number > 1 and retry_state.outcome and not retry_state.outcome.failed:
        logger.info(
            f"[Gemini Retry] Succeeded on attempt {retry_state.attempt_number}/{_GEMINI_MAX_ATTEMPTS}"
        )


# Reusable decorator for all Gemini API calls.
# 6 attempts with exponential backoff: 1s → 2s → 4s → 8s → 16s → 16s (~31s total)
gemini_retry = retry(
    retry=retry_if_exception(_is_gemini_retryable),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(_GEMINI_MAX_ATTEMPTS),
    before_sleep=_log_gemini_before_sleep,
    after=_log_gemini_after,
    reraise=True,
)


_BYTEPLUS_MAX_ATTEMPTS = 6


def _is_byteplus_retryable(exc: BaseException) -> bool:
    """
    Returns True for errors that should be retried against the BytePlus API.
    Handles:
    - SDK 500/timeout/connection errors from AsyncArk client
    - SDK 429 rate-limit errors (ArkRateLimitError / ServerOverloaded)
    - httpx 429/500/502/503/504 errors from direct HTTP path (Seedream 4 suite)
    - String fallback for unexpected exception wrappers
    """
    if isinstance(exc, (ArkInternalServerError, ArkAPITimeoutError, ArkAPIConnectionError)):
        return True
    if isinstance(exc, ArkRateLimitError):
        # 429 ServerOverloaded — transient capacity limit, safe to retry
        return True
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code in (429, 500, 502, 503, 504):
            return True
    error_message = str(exc)
    if (
        "503" in error_message
        or "502" in error_message
        or "500" in error_message
        or "overloaded" in error_message.lower()
        or "ServerOverloaded" in error_message
        or "UNAVAILABLE" in error_message
    ):
        return True
    return False


def _log_byteplus_before_sleep(retry_state: RetryCallState) -> None:
    exc = retry_state.outcome.exception()
    wait = retry_state.next_action.sleep
    logger.warning(
        f"[BytePlus Retry] Attempt {retry_state.attempt_number}/{_BYTEPLUS_MAX_ATTEMPTS} failed | "
        f"{type(exc).__name__}: {exc} | "
        f"waiting {wait:.1f}s → attempt {retry_state.attempt_number + 1}"
    )


def _log_byteplus_after(retry_state: RetryCallState) -> None:
    if retry_state.attempt_number > 1 and retry_state.outcome and not retry_state.outcome.failed:
        logger.info(
            f"[BytePlus Retry] Succeeded on attempt {retry_state.attempt_number}/{_BYTEPLUS_MAX_ATTEMPTS}"
        )


# Reusable decorator for all BytePlus API calls.
# 6 attempts with exponential backoff: 1s → 2s → 4s → 8s → 16s → 16s (~31s total)
byteplus_retry = retry(
    retry=retry_if_exception(_is_byteplus_retryable),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(_BYTEPLUS_MAX_ATTEMPTS),
    before_sleep=_log_byteplus_before_sleep,
    after=_log_byteplus_after,
    reraise=True,
)


_OPENAI_MAX_ATTEMPTS = 6


def _is_openai_retryable(exc: BaseException) -> bool:
    """
    Returns True for errors that should be retried against the OpenAI API.
    Handles:
    - SDK timeout and connection errors
    - 500/502/503/504 status errors from the OpenAI SDK
    - String fallback for unexpected exception wrappers
    """
    if isinstance(exc, (APITimeoutError, APIConnectionError)):
        return True
    if isinstance(exc, APIStatusError) and exc.status_code in (429, 500, 502, 503, 504):
        return True
    if isinstance(exc, RateLimitError):
        return True
    error_message = str(exc)
    if (
        "503" in error_message
        or "502" in error_message
        or "500" in error_message
        or "429" in error_message
        or "overloaded" in error_message.lower()
        or "UNAVAILABLE" in error_message
        or "Bad Gateway" in error_message
    ):
        return True
    return False


def _log_openai_before_sleep(retry_state: RetryCallState) -> None:
    exc = retry_state.outcome.exception()
    wait = retry_state.next_action.sleep
    logger.warning(
        f"[OpenAI Retry] Attempt {retry_state.attempt_number}/{_OPENAI_MAX_ATTEMPTS} failed | "
        f"{type(exc).__name__}: {exc} | "
        f"waiting {wait:.1f}s → attempt {retry_state.attempt_number + 1}"
    )


def _log_openai_after(retry_state: RetryCallState) -> None:
    if retry_state.attempt_number > 1 and retry_state.outcome and not retry_state.outcome.failed:
        logger.info(
            f"[OpenAI Retry] Succeeded on attempt {retry_state.attempt_number}/{_OPENAI_MAX_ATTEMPTS}"
        )


# Reusable decorator for all OpenAI API calls.
# 6 attempts with exponential backoff: 1s → 2s → 4s → 8s → 16s → 16s (~31s total)
openai_retry = retry(
    retry=retry_if_exception(_is_openai_retryable),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(_OPENAI_MAX_ATTEMPTS),
    before_sleep=_log_openai_before_sleep,
    after=_log_openai_after,
    reraise=True,
)


def safe_log_dict(
    data: Dict[str, Any],
) -> str:
    """
    Returns a JSON-safe version of a dict for logging,
    truncating values for specified keys.

    Args:
        data (dict): The dictionary to sanitize
        truncate_keys (Iterable[str]): Keys whose values should be truncated

    Returns:
        str: JSON string with sensitive fields truncated
    """
    safe_data = copy.deepcopy(data)
    truncated_obj = truncate_strings(safe_data)

    return truncated_obj
