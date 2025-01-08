import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
import httpx
from models.search_schema import SearchBoardsResponse,SearchPinsResponse
from constants.url_constants import BASE_URL

load_dotenv()

router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")
    
@router.get("/search/boards", response_model=SearchBoardsResponse)
async def search_boards(
    query: str,
    ad_account_id: Optional[str] = Query(None, max_length=18, regex="^\d+$"),
    bookmark: Optional[str] = Query(None),
    page_size: Optional[int] = Query(25, ge=1, le=250)
):
    """
    Search for boards for the "operation user_account". This includes boards of all board types.
    By default, the "operation user_account" is the token user_account.
    If using Business Access: Specify an ad_account_id to use the owner of that ad_account as the "operation user_account".
    """
    url = f"{BASE_URL}/search/boards"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    params = {"query": query, "page_size": page_size}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    if bookmark:
        params["bookmark"] = bookmark

    try:
        # Make the HTTP GET request to Pinterest API
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            # Return the response in the specified schema format
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Boards not found.")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Unexpected error: {response.text}"
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error while making request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/search/pins", response_model=SearchPinsResponse)
async def search_pins(
    query: str,
    ad_account_id: Optional[str] = Query(None, max_length=18, regex="^\d+$"),
    bookmark: Optional[str] = Query(None),
    page_size: Optional[int] = Query(25, ge=1, le=250)
):
    """
    Search for pins for the "operation user_account". This includes pins for all pin types.
    By default, the "operation user_account" is the token user_account.
    If using Business Access: Specify an ad_account_id to use the owner of that ad_account as the "operation user_account".
    """
    url = f"{BASE_URL}/search/pins"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    params = {"query": query, "page_size": page_size}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    if bookmark:
        params["bookmark"] = bookmark

    try:
        # Make the HTTP GET request to Pinterest API
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response_data = response.json()

            # Ensure missing fields are set to None
            for item in response_data['items']:
                item['pin_metrics'] = item.get('pin_metrics', None)
                item['lifetime_metrics'] = item.get('lifetime_metrics', None)

            return response_data
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Pins not found.")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Unexpected error: {response.text}"
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error while making request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
