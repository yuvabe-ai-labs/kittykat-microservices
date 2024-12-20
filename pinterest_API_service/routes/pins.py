import logging
from fastapi import APIRouter, HTTPException, Depends, Query
import httpx
from pydantic import ValidationError
from dotenv import load_dotenv
from typing import Optional
import os
from models.pins_schema import CreatePinRequest, UpdatePinRequest
from constants.url_constants import BASE_URL

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")
BASE_URL = f"{BASE_URL.rstrip('/')}/pins"
logger.info(f"PINS_BASE_URL: {BASE_URL}")


@router.get("/pins/get-pinterest-pins")
async def get_pinterest_pins():
    """
    Fetch all Pinterest pins.

    Returns:
        List of pins as JSON if the request is successful.
    """
    url = BASE_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }
    logger.info("Fetching Pinterest pins.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            logger.info("Successfully fetched Pinterest pins.")
            return response.json()
        else:
            logger.error(f"Error fetching Pinterest pins. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching Pinterest pins")
    except Exception as e:
        logger.exception("An unexpected error occurred while fetching Pinterest pins.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/pins/create-pin")
async def create_pin(request: CreatePinRequest):
    """
    Create a new pin on a Pinterest board.

    Args:
        request (CreatePinRequest): Payload containing details of the pin to create.

    Returns:
        JSON response with details of the created pin if successful.
    """
    url = BASE_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }

    payload = request.dict(exclude_unset=True)
    logger.info(f"Creating a pin with payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            logger.info("Pin created successfully.")
            return response.json()
        elif response.status_code == 400:
            logger.warning("Invalid pin creation request.")
            raise HTTPException(status_code=400, detail="Invalid pin creation request")
        else:
            logger.error(f"Error creating Pinterest pin. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error creating Pinterest pin")
    except ValidationError as e:
        logger.error("Validation error while creating pin: %s", e.errors())
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}") from e
    except Exception as e:
        logger.exception("An unexpected error occurred while creating the pin.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/pins/{pin_id}")
async def get_pin(pin_id: str, pin_metrics: Optional[bool] = False, ad_account_id: Optional[str] = None):
    """
    Fetch details of a specific pin by its ID.

    Args:
        pin_id (str): The unique ID of the pin.
        pin_metrics (Optional[bool]): Whether to include pin metrics in the response.
        ad_account_id (Optional[str]): Pinterest ad account ID.

    Returns:
        JSON response with details of the pin if found.
    """
    url = f"{BASE_URL}/{pin_id}"
    params = {"pin_metrics": str(pin_metrics).lower()}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }
    logger.info(f"Fetching details for pin ID: {pin_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            logger.info(f"Successfully fetched details for pin ID: {pin_id}")
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Pin with ID {pin_id} not found.")
            raise HTTPException(status_code=404, detail=f"Pin with ID {pin_id} was not found")
        else:
            logger.error(f"Error fetching pin details. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching Pinterest pin")
    except Exception as e:
        logger.exception("An unexpected error occurred while fetching pin details.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.delete("/pins/{pin_id}")
async def delete_pin(pin_id: str, ad_account_id: Optional[str] = None):
    """
    Delete a specific pin by its ID.

    Args:
        pin_id (str): The unique ID of the pin.
        ad_account_id (Optional[str]): Pinterest ad account ID.

    Returns:
        Confirmation message if the pin is deleted successfully.
    """
    url = f"{BASE_URL}/{pin_id}"
    params = {}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }
    logger.info(f"Deleting pin with ID: {pin_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, params=params)

        if response.status_code == 204:
            logger.info(f"Pin with ID {pin_id} deleted successfully.")
            return {"message": "Pin deleted successfully"}
        elif response.status_code == 403:
            logger.warning(f"Not authorized to delete pin with ID: {pin_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this pin")
        elif response.status_code == 404:
            logger.warning(f"Pin with ID {pin_id} not found.")
            raise HTTPException(status_code=404, detail="Pin not found")
        else:
            logger.error(f"Unexpected error deleting pin. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Unexpected error deleting pin")
    except Exception as e:
        logger.exception("An unexpected error occurred while deleting the pin.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.patch("/pins/{pin_id}")
async def update_pin(pin_id: str, pin: UpdatePinRequest, ad_account_id: Optional[str] = None):
    """
    Update details of a specific pin by its ID.

    Args:
        pin_id (str): The unique ID of the pin.
        pin (UpdatePinRequest): Payload containing updated details for the pin.
        ad_account_id (Optional[str]): Pinterest ad account ID.

    Returns:
        JSON response with details of the updated pin if successful.
    """
    url = f"{BASE_URL}/{pin_id}"
    params = {}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }

    payload = pin.dict(exclude_unset=True)
    logger.info(f"Updating pin with ID: {pin_id}, payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, params=params, json=payload)

        if response.status_code == 200:
            logger.info(f"Pin with ID {pin_id} updated successfully.")
            return response.json()
        elif response.status_code == 403:
            logger.warning(f"Not authorized to update pin with ID: {pin_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this pin")
        elif response.status_code == 404:
            logger.warning(f"Pin with ID {pin_id} not found.")
            raise HTTPException(status_code=404, detail="Pin not found")
        else:
            logger.error(f"Unexpected error updating pin. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Unexpected error updating pin")
    except ValidationError as e:
        logger.error("Validation error while updating pin: %s", e.errors())
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}") from e
    except Exception as e:
        logger.exception("An unexpected error occurred while updating the pin.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
