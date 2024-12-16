from fastapi import APIRouter, HTTPException
from uuid import uuid4
from pydantic import ValidationError
from models.schema import HttpUrl, BrandAnalysisResponse, BrandUrlRequest, UrlValidator
from services.brand_utils import generate_brand_json
import json
import logging

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post(
    "/brand/url",
    summary="Analysing a brand from a URL",
    response_model=BrandAnalysisResponse
)
async def get_analysis(request: BrandUrlRequest):
    url = request.url
    request_id = request.request_id
    response_id = str(uuid4())  # Generate a unique response ID

    if not url:
        logger.warning(f"{request_id}, URL is empty, {response_id}")
        return BrandAnalysisResponse(
            brand_name="",
            brand_category=[],
            brand_description="",
            brand_colors=[],
            brand_fonts=[],
            brand_logo=[],
            favicon=[]
        )

    # Validate URL format
    try:
        UrlValidator(url=url)
    except ValidationError:
        logger.warning(
            f"{request_id}, Brand analysis Processing Warning: Invalid URL format: {url}, {response_id}"
        )
        return BrandAnalysisResponse(
            brand_name="",
            brand_category=[],
            brand_description="",
            brand_colors=[],
            brand_fonts=[],
            brand_logo=[],
            favicon=[]
        )

    try:
        logger.info(
            f"{request_id}, Brand analysis Processing started Successfully, {response_id}"
        )
        brand_details = await generate_brand_json(url)
        logger.info(f"{request_id}, Brand details retrieved successfully, {response_id}")

        # Parse JSON-like response
        try:
            brand_data = json.loads(brand_details)
        except json.JSONDecodeError as e:
            logger.error(f"{request_id}, Error decoding brand details JSON: {str(e)}, {response_id}")
            raise HTTPException(status_code=500, detail="Failed to parse brand details JSON")

        logger.info(
            f"{request_id}, Brand analysis Processing Completed Successfully, {response_id}"
        )
        return BrandAnalysisResponse(
            brand_name=brand_data.get("brand_name", ""),
            brand_category=brand_data.get("brand_category", []),
            brand_description=brand_data.get("brand_description", ""),
            brand_colors=brand_data.get("brand_colors", []),
            brand_fonts=brand_data.get("brand_fonts", []),
            brand_logo=brand_data.get("brand_logo", []),
            favicon=brand_data.get("favicon", [])
        )

    except Exception as e:
        logger.error(f"{request_id}, Error extracting brand data: {str(e)}, {response_id}")
        raise HTTPException(
            status_code=500, detail=f"Error extracting brand data: {str(e)}"
        )
