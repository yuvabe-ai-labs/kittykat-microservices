import os
from typing import Dict

# API Configuration
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_KEY")
if not REPLICATE_API_TOKEN:
    print(
        "Warning: Missing Replicate API token! Set REPLICATE_API_KEY as an environment variable."
    )

# API Headers
HEADERS: Dict[str, str] = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json",
}

# Default values
DEFAULT_OWNER = "kittykat-ai"


import requests
from typing import Dict, Any, Optional, Tuple


def make_request(
    method: str, url: str, payload: Optional[Dict[str, Any]] = None
) -> Tuple[int, Dict[str, Any]]:
    """
    Makes HTTP requests to the Replicate API with error handling

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        url: API endpoint URL
        payload: Request payload for POST/PATCH requests

    Returns:
        Tuple of (status_code, response_data)
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, headers=HEADERS)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=payload, headers=HEADERS)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            return 400, {"error": f"Unsupported method: {method}"}

        # Handle successful DELETE requests which return no content
        if response.status_code == 204:
            return 204, {"message": "Operation completed successfully"}

        # Try to parse JSON response if available
        try:
            response_data = response.json() if response.text.strip() else {}
        except requests.exceptions.JSONDecodeError:
            response_data = {"message": response.text}

        return response.status_code, response_data

    except requests.exceptions.RequestException as e:
        return 500, {"error": f"API request failed: {str(e)}"}
