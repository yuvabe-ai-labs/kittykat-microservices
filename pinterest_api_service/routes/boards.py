from fastapi import APIRouter, HTTPException, Depends,Query
import httpx
from dotenv import load_dotenv
import os
from pydantic import ValidationError
from typing import Optional, List
from models.boards_schema import CreateBoardPayload, UpdateBoardPayload
from constants.url_constants import BASE_URL

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")
BASE_URL = f"{BASE_URL.rstrip('/')}/boards"

# Logger setup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/boards/get-pinterest-boards")
async def get_pinterest_boards():
    """
    Fetch all Pinterest boards.

    Returns:
        List of boards if the request is successful.
    Raises:
        HTTPException: If an error occurs while fetching boards.
    """
    url = BASE_URL
    logger.info("Fetching Pinterest boards from URL: %s", url)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        logger.info("Successfully fetched Pinterest boards.")
        return response.json()
    else:
        logger.error("Error fetching Pinterest boards: %s", response.text)
        raise HTTPException(status_code=response.status_code, detail="Error fetching Pinterest boards")

@router.post("/boards/create-boards")
async def create_board(
    payload: CreateBoardPayload,
    ad_account_id: Optional[str] = None
):
    """
    Create a new Pinterest board.

    Args:
        payload (CreateBoardPayload): The payload containing board details.
        ad_account_id (Optional[str]): Ad account ID for the board.

    Returns:
        JSON response of the created board if successful.

    Raises:
        HTTPException: If an error occurs during board creation.
    """
    url = BASE_URL
    params = {}

    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    payload = payload.dict(exclude_unset=True)
    logger.info("Creating a new Pinterest board with payload: %s", payload)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, params=params)

        if response.status_code == 201:
            logger.info("Board created successfully.")
            return response.json()
        elif response.status_code == 400:
            logger.warning("Invalid or duplicated board name.")
            raise HTTPException(
                status_code=400,
                detail="The board name is invalid or duplicated.",
            )
        else:
            logger.error("Unexpected error occurred: %s", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while creating the board.",
            )

    except ValidationError as e:
        logger.error("Validation error: %s", e.errors())
        raise HTTPException(
            status_code=422, detail=f"Validation error: {e.errors()}"
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during board creation.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/boards/{board_id}")
async def get_board(
    board_id: str,
    ad_account_id: Optional[str] = None
):
    """
    Get information about a Pinterest board by its ID.

    Args:
        board_id (str): The unique identifier of the board.
        ad_account_id (Optional[str]): Ad account ID for the board.

    Returns:
        JSON response of the board details if successful.

    Raises:
        HTTPException: If an error occurs during the request.
    """
    url = f"{BASE_URL}/{board_id}"
    params = {}

    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    logger.info("Fetching board details for board ID: %s", board_id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            logger.info("Successfully retrieved board details.")
            return response.json()
        elif response.status_code == 404:
            logger.warning("Board not found.")
            raise HTTPException(
                status_code=404,
                detail="Board not found.",
            )
        else:
            logger.error("Unexpected error occurred: %s", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving the board.",
            )

    except ValidationError as e:
        logger.error("Validation error: %s", e.errors())
        raise HTTPException(
            status_code=422, detail=f"Validation error: {e.errors()}"
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during board retrieval.")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.patch("/boards/{board_id}")
async def update_board(
    board_id: str,
    payload: UpdateBoardPayload,
    ad_account_id: Optional[str] = None,
):
    """
    Update a Pinterest board by its ID.

    Args:
        board_id (str): The unique identifier of the board.
        payload (UpdateBoardPayload): The payload containing updated board details.
        ad_account_id (Optional[str]): Ad account ID for the board.

    Returns:
        JSON response of the updated board if successful.

    Raises:
        HTTPException: If an error occurs during the update.
    """
    url = f"{BASE_URL}/{board_id}"
    params = {}

    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    payload_dict = payload.dict(exclude_unset=True)
    logger.info("Updating board ID %s with payload: %s", board_id, payload_dict)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=payload_dict, params=params)

        if response.status_code == 200:
            logger.info("Board updated successfully.")
            return response.json()
        elif response.status_code == 400:
            logger.warning("Invalid board parameters.")
            raise HTTPException(
                status_code=400,
                detail="Invalid board parameters."
            )
        elif response.status_code == 403:
            logger.warning("Not authorized to update this board.")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update this board."
            )
        elif response.status_code == 404:
            logger.warning("Board not found.")
            raise HTTPException(
                status_code=404,
                detail="Board not found."
            )
        else:
            logger.error("Unexpected error occurred: %s", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while updating the board."
            )

    except Exception as e:
        logger.exception("Unexpected error during board update.")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}")

@router.delete("/boards/{board_id}")
async def delete_board(
    board_id: str,
    ad_account_id: Optional[str] = None,
):
    """
    Delete a Pinterest board by its ID.

    Args:
        board_id (str): The unique identifier of the board.
        ad_account_id (Optional[str]): Ad account ID for the board.

    Returns:
        Success message if the board is deleted.

    Raises:
        HTTPException: If an error occurs during the deletion.
    """
    url = f"{BASE_URL}/{board_id}"
    params = {}

    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    logger.info("Deleting board ID: %s", board_id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, params=params)

        if response.status_code == 204:
            logger.info("Board deleted successfully.")
            return {"detail": "Board deleted successfully"}
        elif response.status_code == 403:
            logger.warning("Not authorized to delete this board.")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this board."
            )
        elif response.status_code == 404:
            logger.warning("Board not found.")
            raise HTTPException(
                status_code=404,
                detail="Board not found."
            )
        elif response.status_code == 409:
            logger.warning("Could not get exclusive access to delete the board.")
            raise HTTPException(
                status_code=409,
                detail="Could not get exclusive access to delete the board."
            )
        elif response.status_code == 429:
            logger.warning("Rate limit exceeded.")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        else:
            logger.error("Unexpected error occurred: %s", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while deleting the board."
            )

    except Exception as e:
        logger.exception("Unexpected error during board deletion.")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/boards/{board_id}/pins")
async def list_pins_on_board(
    board_id: str,
    bookmark: Optional[str] = None,
    page_size: Optional[int] = 25,
    creative_types: Optional[List[str]] = Query(None),  # Use Query to ensure it's treated as query parameter
    ad_account_id: Optional[str] = None,
    pin_metrics: Optional[bool] = False,
):
    """
    Fetch all Pins on a specified Pinterest board.

    Args:
        board_id (str): Unique identifier of the board.
        bookmark (Optional[str]): Cursor for pagination.
        page_size (Optional[int]): Maximum number of items to include in the response (default: 25).
        creative_types (Optional[List[str]]): Filter Pins by creative types (e.g., REGULAR, VIDEO).
        ad_account_id (Optional[str]): ID of the ad account for business access.
        pin_metrics (Optional[bool]): Whether to return 90d and lifetime Pin metrics.

    Returns:
        JSON response with the list of Pins if successful.

    Raises:
        HTTPException: If an error occurs during the request.
    """
    url = f"{BASE_URL}/{board_id}/pins"

    # Construct query parameters
    params = {
        "bookmark": bookmark,
        "page_size": page_size,
        "creative_types": ",".join(creative_types) if creative_types else None,
        "ad_account_id": ad_account_id,
        "pin_metrics": str(pin_metrics).lower(),
    }
    params = {key: value for key, value in params.items() if value is not None}

    headers = {
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    logger.info(f"Fetching Pins for board ID: {board_id} with params: {params}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            logger.info("Successfully fetched Pins for board.")
            return response.json()
        elif response.status_code == 404:
            logger.warning("Board not found.")
            raise HTTPException(status_code=404, detail="Board not found.")
        else:
            logger.error(
                f"Error fetching Pins for board. Status code: {response.status_code}, Response: {response.text}"
            )
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while fetching Pins.",
            )
    except Exception as e:
        logger.exception("An unexpected error occurred while fetching Pins.")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )
