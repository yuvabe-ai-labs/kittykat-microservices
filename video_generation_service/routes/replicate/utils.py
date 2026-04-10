
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel
from config.env import env
import httpx


async def make_request(
    method: str,
    url: str,
    payload: Optional[Dict[str, Any] | str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    is_search: bool = False,
) -> Tuple[int, Dict[str, Any]]:
    """
    Makes HTTP requests to the Replicate API with error handling

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        url: API endpoint URL
        payload: Request payload for POST/PATCH requests
        custom_headers: Additional headers to include in the request
        params: Query parameters for GET requests
        is_search: Whether this is a search request (uses special handling)

    Returns:
        Tuple of (status_code, response_data)
    """
    # Prepare headers by combining default headers with custom headers
    request_headers = {
        "Authorization": f"Bearer {env.REPLICATE_API_KEY}",
        "Content-Type": "application/json",
    }
    if custom_headers:
        request_headers.update(custom_headers)

    try:
        async with httpx.AsyncClient() as client:
            if is_search:
                # Special handling for search requests which use a QUERY method
                # We'll simulate this with a POST request with text/plain content type
                request_headers["Content-Type"] = "text/plain"
                response = await client.post(
                    url, data=payload, headers=request_headers)
            elif method.upper() == "GET":
                response = await client.get(
                    url, headers=request_headers, params=params)
            elif method.upper() == "POST":
                if isinstance(payload, str):
                    response = await client.post(
                        url, data=payload, headers=request_headers)
                else:
                    response = await client.post(
                        url, json=payload, headers=request_headers)
            elif method.upper() == "PATCH":
                response = await client.patch(
                    url, json=payload, headers=request_headers)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=request_headers)
            else:
                return 400, {"error": f"Unsupported method: {method}"}

            # Handle successful DELETE requests which return no content
            if response.status_code == 204:
                return 204, {"message": "Operation completed successfully"}

            # Try to parse JSON response if available
            try:
                response_data = response.json() if response.text.strip() else {}
            except Exception:
                response_data = {"message": response.text}

            return response.status_code, response_data

    except httpx.RequestError as e:
        return 500, {"error": f"API request failed: {str(e)}"}
