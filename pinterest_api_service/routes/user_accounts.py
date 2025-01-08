from fastapi import APIRouter, HTTPException,Query,Body
import httpx
from dotenv import load_dotenv
import os
from typing import Optional, List
from pydantic import ValidationError
from constants.url_constants import BASE_URL
from models.user_accounts_schema import UserAccountResponse
import logging
from datetime import datetime

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")
BASE_URL = f"{BASE_URL.rstrip('/')}/user_account"



@router.get("/user_account", response_model=UserAccountResponse)
async def get_user_account(ad_account_id: Optional[str] = Query(None, max_length=18, regex=r"^\d+$")):
    """
    Get account information for the "operation user_account".
    
    Args:
        ad_account_id (Optional[str]): Unique identifier of an ad account. If provided, uses the owner of that ad account as the "operation user_account".

    Returns:
        UserAccountResponse: Account information for the user account.

    Raises:
        HTTPException: If the user account is not authorized or an error occurs.
    """
    params = {}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}"
    }

    logger.info(f"Fetching user account details with ad_account_id: {ad_account_id if ad_account_id else 'None'}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            logger.info("Successfully fetched user account details.")
            return response.json()
        elif response.status_code == 403:
            logger.warning("Not authorized to access the user account.")
            raise HTTPException(status_code=403, detail="Not authorized to access the user account.")
        else:
            logger.error(f"Error fetching user account. Status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching user account details.")
    except httpx.RequestError as e:
        logger.exception("An HTTP request error occurred.")
        raise HTTPException(status_code=500, detail=f"HTTP request error: {str(e)}")
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    

@router.get("/user_account/analytics")
async def get_user_account_analytics(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,  # Format: YYYY-MM-DD
    from_claimed_content: Optional[str] = "BOTH",  # Enum: "OTHER", "CLAIMED", "BOTH"
    pin_format: Optional[str] = "ALL",  # Enum: "ALL", "ORGANIC_IMAGE", "ORGANIC_PRODUCT", etc.
    app_types: Optional[str] = "ALL",  # Enum: "ALL", "MOBILE", "TABLET", "WEB"
    content_type: Optional[str] = "ALL",  # Enum: "ALL", "PAID", "ORGANIC"
    source: Optional[str] = "ALL",  # Enum: "ALL", "YOUR_PINS", "OTHER_PINS"
    metric_types: Optional[List[str]] = [],  # List of metric types to get data for
    split_field: Optional[str] = "NO_SPLIT",  # Enum: "NO_SPLIT", "APP_TYPE", "OWNED_CONTENT", etc.
    ad_account_id: Optional[str] = None,  # Ad account identifier (optional)
):
    """
    Get analytics for the "operation user_account".
    By default, the "operation user_account" is the token user_account.
    """

    url = f"{BASE_URL}/analytics"
    # Validate the date range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        if (end_date_obj - start_date_obj).days > 90:
            raise HTTPException(status_code=400, detail="The date range cannot exceed 90 days.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected format: YYYY-MM-DD.")
    
    
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "from_claimed_content": from_claimed_content,
        "pin_format": pin_format,
        "app_types": app_types,
        "content_type": content_type,
        "source": source,
        "metric_types": ",".join(metric_types),  # Converting list to comma-separated string
        "split_field": split_field,
        "ad_account_id": ad_account_id
    }
    params = {k: v for k, v in params.items() if v is not None}  # Remove None values from params

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved user account analytics
        elif response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail="Invalid user accounts analytics parameters."
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access the user account analytics."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving user account analytics."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

@router.get("/user_account/analytics/top_pins")
async def get_top_pins_analytics(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,  # Format: YYYY-MM-DD
    sort_by: str,  # Enum: "ENGAGEMENT", "IMPRESSION", "OUTBOUND_CLICK", etc.
    from_claimed_content: Optional[str] = "BOTH",  # Enum: "OTHER", "CLAIMED", "BOTH"
    pin_format: Optional[str] = "ALL",  # Enum: "ALL", "ORGANIC_IMAGE", "ORGANIC_PRODUCT", etc.
    app_types: Optional[str] = "ALL",  # Enum: "ALL", "MOBILE", "TABLET", "WEB"
    content_type: Optional[str] = "ALL",  # Enum: "ALL", "PAID", "ORGANIC"
    source: Optional[str] = "ALL",  # Enum: "ALL", "YOUR_PINS", "OTHER_PINS"
    metric_types: Optional[List[str]] = [],  # List of metric types to get data for
    num_of_pins: Optional[int] = 10,  # Number of pins to retrieve, default is 10, max is 50
    created_in_last_n_days: Optional[int] = None,  # Filter pins created in the last n days
    ad_account_id: Optional[str] = None,  # Ad account ID for business access
):
    """
    Get analytics data about the user's top pins (limited to the top 50).
    By default, the "operation user_account" is the token user_account.
    Optional: Specify an ad_account_id to use the owner of that ad_account as the "operation user_account".
    """
    url = f"{BASE_URL}/analytics/top_pins"
    
    # Validate the date range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        if (end_date_obj - start_date_obj).days > 90:
            raise HTTPException(status_code=400, detail="The date range cannot exceed 90 days.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected format: YYYY-MM-DD.")

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "sort_by": sort_by,
        "from_claimed_content": from_claimed_content,
        "pin_format": pin_format,
        "app_types": app_types,
        "content_type": content_type,
        "source": source,
        "metric_types": ",".join(metric_types),  # Converting list to comma-separated string
        "num_of_pins": num_of_pins,
        "created_in_last_n_days": created_in_last_n_days,
        "ad_account_id": ad_account_id,
    }
    
    params = {k: v for k, v in params.items() if v is not None}  # Remove None values from params

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved top pins analytics
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access the user account analytics."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving top pins analytics."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/user_account/analytics/top_video_pins")
async def get_top_video_pins_analytics(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,  # Format: YYYY-MM-DD
    sort_by: str,  #  Specify sorting order for video metrics: Enum: "IMPRESSION", "SAVE", "OUTBOUND_CLICK", "VIDEO_MRC_VIEW", "VIDEO_AVG_WATCH_TIME", "VIDEO_V50_WATCH_TIME", "QUARTILE_95_PERCENT_VIEW", "VIDEO_10S_VIEW", "VIDEO_START"
    from_claimed_content: Optional[str] = "BOTH",  # Enum: "OTHER", "CLAIMED", "BOTH"
    pin_format: Optional[str] = "ALL",  # Enum: "ALL", "ORGANIC_IMAGE", etc.
    app_types: Optional[str] = "ALL",  # Enum: "ALL", "MOBILE", "TABLET", "WEB"
    content_type: Optional[str] = "ALL",  # Enum: "ALL", "PAID", "ORGANIC"
    source: Optional[str] = "ALL",  # Enum: "ALL", "YOUR_PINS", "OTHER_PINS"
    metric_types: Optional[List[str]] = [],  # List of video metric types to retrieve
    num_of_pins: Optional[int] = 10,  # Default is 10, max is 50
    created_in_last_n_days: Optional[int] = None,  # Get metrics for pins created in the last "n" days
    ad_account_id: Optional[str] = None,  # Optional ad account ID
):
    """
    Get analytics data about a user's top video pins (limited to the top 50).
    """
    url = f"{BASE_URL}/analytics/top_video_pins"

    # Validate the date range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        if (end_date_obj - start_date_obj).days > 90:
            raise HTTPException(status_code=400, detail="The date range cannot exceed 90 days.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected format: YYYY-MM-DD.")

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "sort_by": sort_by,
        "from_claimed_content": from_claimed_content,
        "pin_format": pin_format,
        "app_types": app_types,
        "content_type": content_type,
        "source": source,
        "metric_types": ",".join(metric_types),  # Convert list to a comma-separated string
        "num_of_pins": num_of_pins,
        "created_in_last_n_days": created_in_last_n_days,
        "ad_account_id": ad_account_id,
    }

    params = {k: v for k, v in params.items() if v is not None}  # Remove None values from parameters

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved top video pins analytics
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access the user account analytics."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving top video pins analytics."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

@router.get("/user_account/businesses")
async def list_linked_businesses():
    """
    Get a list of linked business accounts.
    """
    url = f"{BASE_URL}/businesses"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved linked business accounts
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving linked business accounts.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user_account/followers")
async def list_followers(
    bookmark: Optional[str] = Query(None, description="Cursor used to fetch the next page of items"),
    page_size: int = Query(25, ge=1, le=250, description="Maximum number of items to include in a single page (1-250)")
):
    """
    Get a list of your followers.
    """
    url = f"{BASE_URL}/followers"
    params = {
        "page_size": page_size
    }

    # Only add 'bookmark' to the params if it's not empty or None
    if bookmark:
        params["bookmark"] = bookmark
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved followers
        elif response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail="Invalid user id or request parameters."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving followers."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user_account/following")
async def list_following(
    bookmark: Optional[str] = Query(None, description="Cursor used to fetch the next page of items"),
    page_size: int = Query(25, ge=1, le=250, description="Maximum number of items to include in a single page (1-250)"),
    feed_type: str = Query("ALL", description="Specifies the type of followees to be filtered", enum=["ALL", "RANKED", "CREATOR_ONLY", "RANKED_CREATOR_ONLY"]),
    explicit_following: bool = Query(False, description="Include only explicit follows when true"),
    ad_account_id: Optional[str] = Query(None, max_length=18, regex="^\\d+$", description="Unique identifier of an ad account")
):
    """
    Get a list of who a certain user follows.
    """
    url = f"{BASE_URL}/following"
    params = {
        "page_size": page_size,
        "feed_type": feed_type,
        "explicit_following": explicit_following,
    }

    # Only add 'bookmark' to the params if it's not empty or None
    if bookmark:
        params["bookmark"] = bookmark

    if ad_account_id:
        params["ad_account_id"]= ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved followees
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving followers."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user_account/following/boards")
async def list_following_boards(
    bookmark: Optional[str] = Query(
        None, description="Cursor used to fetch the next page of items"
    ),
    page_size: int = Query(
        25, ge=1, le=250, description="Maximum number of items to include in a single page (1-250)"
    ),
    explicit_following: bool = Query(
        False, description="Include only explicit follows when true"
    ),
    ad_account_id: Optional[str] = Query(
        None, max_length=18, regex="^\\d+$", description="Unique identifier of an ad account"
    )
):
    """
    Get a list of boards a user follows.
    """
    url = f"{BASE_URL}/following/boards"
    params = {
        "page_size": page_size,
        "explicit_following": explicit_following,
    }

    # Only add 'bookmark' to the params if it's not empty or None
    if bookmark:
        params["bookmark"] = bookmark

    if ad_account_id:
        params["ad_account_id"]= ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved boards
        elif response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID or parameters provided."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving boards."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )



@router.post("/user_account/websites")
async def verify_website(
    website: str = Body(..., description="The website URL to verify"),
    verification_method: str = Body("METATAG", description="Verification method. Default is METATAG."),
    ad_account_id: Optional[str] = Query(None, max_length=18, regex="^\\d+$", description="Unique identifier of an ad account (optional)")
):
    """
    Verify a website as a signed-in user.
    """
    # Verify that the verification method is one of the allowed options
    allowed_methods = ["FILENAME", "METATAG", "DNSTXT"]
    if verification_method not in allowed_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification method. Allowed values: {', '.join(allowed_methods)}"
        )

    url = f"{BASE_URL}/websites"
    payload = {
        "website": website,
        "verification_method": verification_method
    }

    # Optional ad_account_id can be added to the payload if provided
    if ad_account_id:
        payload["ad_account_id"] = ad_account_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()  # Successfully verified website
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while verifying the website."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user_account/websites")
async def get_user_websites(
    bookmark: Optional[str] = Query(None, description="Cursor used to fetch the next page of items"),
    page_size: Optional[int] = Query(25, ge=1, le=250, description="Maximum number of items to include in a single page")
):
    """
    Get the list of user websites, claimed or not.
    """
    url = f"{BASE_URL}/websites"
    
    # Initialize params with the page_size parameter
    params = {
        "page_size": page_size
    }
    
    # Only add 'bookmark' to the params if it's not empty or None
    if bookmark:
        params["bookmark"] = bookmark

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()  # Successfully retrieved user websites
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access the user website list."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving the websites."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )




@router.delete("/user_account/websites")
async def unverify_website(website: str):
    """
    Unverify a website that was previously verified by the signed-in user.
    """
    url = f"{BASE_URL}/websites"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }
    
    params = {
        "website": website
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, params=params)

        if response.status_code == 204:
            return {"detail": "Successfully unverified website."}
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Website not in user list."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while unverifying the website."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user_account/websites/verification")
async def get_verification_code(ad_account_id: Optional[str] = None):
    """
    Get verification code for website claiming.
    """
    url = f"{BASE_URL}/websites/verification"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }
    
    params = {}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access the user verification code for website claiming."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while getting the verification code."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )



@router.get("/users/{username}/interests/follow")
async def list_following_interests(username: str, bookmark: Optional[str] = None, page_size: Optional[int] = 25):
    """
    Get a list of a user's following interests.
    """
    # Remove '/user_account' from the BASE_URL
    interests_url = BASE_URL.replace('/user_account', '')
    url = f"{interests_url}/users/{username}/interests/follow"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }
    
    params = {
        "page_size": page_size,
    }

    if bookmark:
        params["bookmark"]= bookmark
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail="Invalid parameters."
            )
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Authorization failed."
            )
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while fetching the following interests."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
