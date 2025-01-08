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
BASE_URL = f"{BASE_URL.rstrip('/')}/ad_accounts"


@router.get("/ad_accounts")
async def list_ad_accounts(
    bookmark: Optional[str] = None, 
    page_size: Optional[int] = 25, 
    include_shared_accounts: Optional[bool] = True
):
    """
    Get a list of ad accounts the user has access to.
    """
    url = BASE_URL
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }
    
    params = {
        "page_size": page_size,
        "include_shared_accounts": str(include_shared_accounts).lower(),  # Ensure boolean is passed as a string
    }

    if bookmark:
        params["bookmark"]= bookmark
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
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



@router.post("/ad_accounts")
async def create_ad_account(ad_account: AdAccountCreateRequest):
    """
    Create a new ad account with the provided details.
    """
    url = BASE_URL
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to create an ad account
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=ad_account.dict())

        if response.status_code == 200:
            return response.json()
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
    

@router.get("/ad_accounts/{ad_account_id}")
async def get_ad_account(ad_account_id: str):
    """
    Get the details of an ad account by its ID.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )

    url = f"{BASE_URL}/{ad_account_id}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch the ad account details
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
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

@router.get("/ad_accounts/{ad_account_id}/analytics")
async def get_ad_account_analytics(
    ad_account_id: str,
    start_date: str,
    end_date: str,
    columns: List[str],
    granularity: str = "TOTAL",  # Default to "TOTAL"
    click_window_days: int = 30,  # Default to 30
    engagement_window_days: int = 30,  # Default to 30
    view_window_days: int = 1,  # Default to 1
    conversion_report_time: str = "TIME_OF_AD_ACTION"  # Default to "TIME_OF_AD_ACTION"
):
    """
    Get analytics for a specified ad account with filtering options.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    # Validate dates
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Dates must be in YYYY-MM-DD format."
        )

    if (end_date_obj - start_date_obj).days > 90:
        raise HTTPException(
            status_code=400,
            detail="The time range cannot exceed 90 days."
        )

    # Construct the query parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "columns": ",".join(columns),
        "granularity": granularity,
        "click_window_days": click_window_days,
        "engagement_window_days": engagement_window_days,
        "view_window_days": view_window_days,
        "conversion_report_time": conversion_report_time,
    }

    url = f"{BASE_URL}/{ad_account_id}/analytics"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch the ad account analytics
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
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