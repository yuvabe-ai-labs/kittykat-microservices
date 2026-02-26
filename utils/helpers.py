import copy
from typing import Any, Dict
from fastapi import HTTPException, Header
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, RetryCallState
from google.api_core.exceptions import (
    ServiceUnavailable,
    InternalServerError,
    DeadlineExceeded,
    BadGateway,
)
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


def _is_gemini_retryable(exc: BaseException) -> bool:
    """
    Returns True for errors that should be retried against the Gemini API.
    Handles:
    - Google API 503/500/502/504 transport errors
    - SDK AttributeError bug: 503 responses with a string 'error' value cause
      AttributeError: 'str' object has no attribute 'get' in _api_client.py
    """
    try:

        if isinstance(
            exc, (ServiceUnavailable, InternalServerError, DeadlineExceeded, BadGateway)
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
        or "overloaded" in error_message.lower()
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
