import copy
from typing import Any, Dict
from fastapi import HTTPException, Header


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
