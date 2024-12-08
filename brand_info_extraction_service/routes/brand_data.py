from fastapi import APIRouter, HTTPException
from models.brand_data import BrandDataRequest, BrandDataResponse
from helpers.brand_data import extract_brand_data
from urllib.parse import urlparse

router = APIRouter()


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all(
            [result.scheme, result.netloc]
        )  # Ensure the URL has a scheme (http/https) and netloc (domain)
    except Exception:
        return False


@router.post("/data", response_model=BrandDataResponse)
async def get_brand_data(request: BrandDataRequest):
    try:
        result = await extract_brand_data(request.url)

        # Validate brand logo and favicon URLs
        brand_logo = result.get("brand_logo")
        favicon = result.get("favicon")

        # Ensure only valid URLs are returned
        return BrandDataResponse(
            brand_name=result["brand_name"],
            brand_category=result.get("brand_category", None),
            brand_description=result.get("brand_description", None),
            brand_logo=brand_logo if brand_logo and is_valid_url(brand_logo) else None,
            brand_colors=result.get("brand_colors", None),
            brand_fonts=result.get("brand_fonts", None),
            favicon=favicon if favicon and is_valid_url(favicon) else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting brand data: {str(e)}"
        )
