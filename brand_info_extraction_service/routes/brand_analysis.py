from fastapi import APIRouter,HTTPException
from uuid import uuid4
from pydantic import ValidationError
from models.schema import HttpUrl,BrandAnalysisResponse,BrandUrlRequest,UrlValidator
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
        return BrandAnalysisResponse(
            brand_name="",
            brand_category=[],
            brand_description="",
            brand_colors=[],
            brand_fonts=[],
            brand_logo=[],
            favicon= []
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
            favicon= []
        )

    try:
        brand_details = await generate_brand_json( url)

        # Extract JSON-like content
        start_index = brand_details.find("{")
        end_index = brand_details.rfind("}") + 1
        json_string = brand_details[start_index:end_index]
        output = json.loads(json_string)

        logger.info(
            f"{request_id}, Brand analysis Processing Completed Successfully, {response_id}"
        )
        return BrandAnalysisResponse(
            brand_name=output["brand_name"],
            brand_category=output["brand_category"],
            brand_description=output["brand_description"],
            brand_colors=output["brand_colors"],
            brand_fonts=output["brand_fonts"],
            brand_logo=output["brand_logo"],
            favicon= output["favicon"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting brand data: {str(e)}"
        )