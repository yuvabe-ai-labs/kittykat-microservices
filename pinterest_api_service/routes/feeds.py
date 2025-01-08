from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import List
from datetime import date
from typing import Optional
from constants.url_constants import BASE_URL
from dotenv import load_dotenv
from models.ad_accounts_schema import AdAccountCreateRequest

# Load environment variables from .env file
load_dotenv()


router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")


@router.get("/catalogs/feeds")
async def list_feeds(
    bookmark: Optional[str] = None,
    page_size: Optional[int] = 25,
    catalog_id: Optional[str] = None,
    ad_account_id: Optional[str] = None
):
    """
    List feeds owned by the "operation user_account". Optionally filter by catalog_id and ad_account_id.
    """
    # Validate page_size range
    if not (1 <= page_size <= 250):
        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 250."
        )

    # Validate ad_account_id if provided (numeric and <= 18 characters)
    if ad_account_id and (len(ad_account_id) > 18 or not ad_account_id.isdigit()):
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    # Construct the URL with query parameters
    url = f"{BASE_URL}/catalogs/feeds"
    params = {
        "bookmark": bookmark,
        "page_size": page_size,
        "catalog_id": catalog_id,
        "ad_account_id": ad_account_id,
    }

    # Filter out None values from the parameters
    params = {k: v for k, v in params.items() if v is not None}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch the list of feeds
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Return the feeds data
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error occurred: {response.json().get('message', 'Unexpected error')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )