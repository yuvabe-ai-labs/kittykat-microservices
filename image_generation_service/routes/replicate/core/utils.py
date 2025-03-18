from typing import Dict, Any, Optional
from core.utils import BaseApiResponse


def create_response(
    status_code: int, message: str, data: Optional[Any] = None
) -> BaseApiResponse:
    """
    Creates a standardized API response

    Args:
        status_code: HTTP status code
        message: Response message
        data: Optional response data

    Returns:
        BaseApiResponse object
    """
    return BaseApiResponse(status_code=status_code, message=message, data=data)


def format_model_response(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format model data for response"""
    return {
        "id": model_data.get("id", ""),
        "owner": model_data.get("owner", ""),
        "name": model_data.get("name", ""),
        "visibility": model_data.get("visibility", ""),
        "hardware": model_data.get("hardware", ""),
        "latest_version": model_data.get("latest_version", {}),
    }


def format_deployment_response(deployment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format deployment data for response"""
    return {
        "id": deployment_data.get("id", ""),
        "name": deployment_data.get("name", ""),
        "model": deployment_data.get("model", ""),
        "version": deployment_data.get("version", ""),
        "status": deployment_data.get("status", ""),
        "hardware": deployment_data.get("hardware", ""),
        "min_instances": deployment_data.get("min_instances", 1),
        "max_instances": deployment_data.get("max_instances", 1),
        "autoscale": deployment_data.get("autoscale", False),
        "cloud": deployment_data.get("cloud", ""),
    }


def format_prediction_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats prediction response data to match our API schema.

    Args:
        response_data: Raw API response data.

    Returns:
        Formatted prediction data.
    """
    return {
        "id": response_data.get("id"),
        "model": response_data.get("model"),
        "version": response_data.get("version"),
        "input": response_data.get("input", {}),
        "logs": response_data.get("logs"),
        "output": response_data.get("output"),
        "error": response_data.get("error"),
        "status": response_data.get("status"),
        "created_at": response_data.get("created_at"),
        "started_at": response_data.get("started_at"),
        "completed_at": response_data.get("completed_at"),
        "data_removed": response_data.get("data_removed", False),
        "metrics": response_data.get("metrics", {}),
        "urls": {
            "get": response_data["urls"].get("get"),
            "cancel": response_data["urls"].get("cancel"),
            "stream": response_data["urls"].get("stream"),
        },
        "source": response_data.get("source"),
    }
