from fastapi import APIRouter, HTTPException,Query
import httpx
import os
from typing import List
from datetime import date
from typing import Optional
from constants.url_constants import BASE_URL
from dotenv import load_dotenv
from models.campaigns_schema import CreateCampaignRequest,UpdateCampaignRequest

# Load environment variables from .env file
load_dotenv()


router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")

@router.get("/ad_accounts/{ad_account_id}/campaigns")
async def list_campaigns(
    ad_account_id: str,
    campaign_ids: Optional[List[str]] = None,
    entity_statuses: Optional[List[str]] = None,
    page_size: int = 25,  # Default to 25
    order: str = "ASCENDING",  # Default to "ASCENDING"
    bookmark: Optional[str] = None
):
    """
    Get a list of campaigns in a specific ad account.
    Filters campaigns based on optional query parameters.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    # Construct the query parameters
    params = {
        "page_size": page_size,
        "order": order,
    }

    if bookmark:
        params["bookmark"]= bookmark

    if campaign_ids:
        params["campaign_ids"] = ",".join(campaign_ids)
    
    if entity_statuses:
        params["entity_statuses"] = ",".join(entity_statuses)

    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch the campaigns
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
    

@router.post("/ad_accounts/{ad_account_id}/campaigns")
async def create_campaigns(
    ad_account_id: str,
    campaign_request: CreateCampaignRequest
):
    """
    Create multiple campaigns for the specified ad account.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )

    # Prepare the request payload
    payload = campaign_request.dict()

    # Construct the URL
    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to create the campaigns
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()  # Return the successful response
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

@router.patch("/ad_accounts/{ad_account_id}/campaigns")
async def update_campaigns(
    ad_account_id: str,
    campaign_request: UpdateCampaignRequest
):
    """
    Update multiple campaigns for the specified ad account.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )

    # Prepare the request payload
    payload = campaign_request.dict()

    # Construct the URL
    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to update the campaigns
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()  # Return the successful response
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
    

@router.get("/ad_accounts/{ad_account_id}/campaigns/analytics")
async def get_campaign_analytics(
    ad_account_id: str,
    start_date: str,
    end_date: str,
    campaign_ids: List[str],
    columns: List[str],
    granularity: str,
    click_window_days: int = 30,
    engagement_window_days: int = 30,
    view_window_days: int = 1,
    conversion_report_time: str = "TIME_OF_AD_ACTION"
):
    """
    Fetch analytics for the specified campaigns in an ad account.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    # Validate the date format (YYYY-MM-DD)
    try:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Dates must be in YYYY-MM-DD format."
        )

    # Validate the granularity value
    if granularity not in ["TOTAL", "DAY", "HOUR", "WEEK", "MONTH"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid granularity. Must be one of: 'TOTAL', 'DAY', 'HOUR', 'WEEK', 'MONTH'."
        )

    # Construct the URL
    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns/analytics"

    # Prepare query parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "campaign_ids": ",".join(campaign_ids),
        "columns": ",".join(columns),
        "granularity": granularity,
        "click_window_days": click_window_days,
        "engagement_window_days": engagement_window_days,
        "view_window_days": view_window_days,
        "conversion_report_time": conversion_report_time,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch campaign analytics
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Return the successful response
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
    
@router.get("/ad_accounts/{ad_account_id}/campaigns/targeting_analytics")
async def get_targeting_analytics(
    ad_account_id: str,
    campaign_ids: List[str] = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    targeting_types: List[str] = Query(...),
    columns: List[str] = Query(...),
    granularity: str = Query(...),
    click_window_days: int = Query(30, ge=1, le=60),
    engagement_window_days: int = Query(30, ge=1, le=60),
    view_window_days: int = Query(1, ge=1, le=60),
    conversion_report_time: str = Query("TIME_OF_AD_ACTION", regex="^(TIME_OF_AD_ACTION|TIME_OF_CONVERSION)$"),
    attribution_types: str = Query("INDIVIDUAL", regex="^(INDIVIDUAL|HOUSEHOLD)$")
):
    """
    Fetch targeting analytics for one or more campaigns in an ad account.
    """
    # Validate ad_account_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    # Validate the date format (YYYY-MM-DD)
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Dates must be in YYYY-MM-DD format."
        )

    # Validate granularity value
    if granularity not in ["TOTAL", "DAY", "HOUR", "WEEK", "MONTH"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid granularity. Must be one of: 'TOTAL', 'DAY', 'HOUR', 'WEEK', 'MONTH'."
        )

    # Construct the URL
    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns/targeting_analytics"

    # Prepare query parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "campaign_ids": ",".join(campaign_ids),
        "targeting_types": ",".join(targeting_types),
        "columns": ",".join(columns),
        "granularity": granularity,
        "click_window_days": click_window_days,
        "engagement_window_days": engagement_window_days,
        "view_window_days": view_window_days,
        "conversion_report_time": conversion_report_time,
        "attribution_types": attribution_types,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch targeting analytics
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Return the successful response
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
    

@router.get("/ad_accounts/{ad_account_id}/campaigns/{campaign_id}")
async def get_campaign(ad_account_id: str, campaign_id: str):
    """
    Fetch details of a specific campaign based on the ad account ID and campaign ID.
    """
    # Validate ad_account_id and campaign_id length (<= 18 characters and must be numeric)
    if len(ad_account_id) > 18 or not ad_account_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ad_account_id. It must be a number with no more than 18 digits."
        )
    
    if len(campaign_id) > 18 or not campaign_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid campaign_id. It must be a number with no more than 18 digits."
        )
    
    # Construct the URL
    url = f"{BASE_URL}/ad_accounts/{ad_account_id}/campaigns/{campaign_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        # Send the request to fetch the specific campaign details
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return the campaign data
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