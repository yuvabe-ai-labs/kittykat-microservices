from fastapi import APIRouter
from services.gcp import upload_to_gcp
from models.global_models import GeneralResponse
from models.replicate_models import ImageRequest
from services.enhance_prompt import enhance_prompt
from services.replicate import generate_prediction
from config.logger import logger

router = APIRouter()


@router.post("/replicate/image/generate", response_model=GeneralResponse)
async def generate_image(request: ImageRequest):
    """
    Generate an image based on the provided prompt using the Replicate API and upload to GCP.
    If enhance_prompt is True, the prompt is first enhanced using the OpenAI enhancement service.
    """
    try:
        # Enhance the prompt if requested
        enhanced_prompt = request.prompt
        if request.enhance_prompt:
            try:
                logger.info("Enhancing the prompt...")
                enhanced_prompt = await enhance_prompt(request.prompt)
            except Exception as e:
                logger.error(f"Prompt enhancement failed: {str(e)}")
                return GeneralResponse(
                    status_code=500,
                    data=None,
                    message=str(e),
                )

        # Generate image using the (enhanced) prompt
        try:
            logger.info("Generating prediction...")
            prediction = generate_prediction(request.model, enhanced_prompt)
        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            return GeneralResponse(
                status_code=500,
                data=None,
                message=str(e),
            )

        # Handle prediction result
        if prediction.status == "succeeded":
            logger.info("Prediction succeeded, uploading to GCP...")
            gcp_url = upload_to_gcp(
                prediction.output[0],
                f"replicate_outputs/{prediction.id}.webp",
            )

            response_data = {
                "asset_url": gcp_url,
                "asset_info": {
                    "model": prediction.model,
                    "created_at": prediction.created_at,
                    "started_at": prediction.started_at,
                    "completed_at": prediction.completed_at,
                    "status": prediction.status,
                    "metrics": prediction.metrics,
                    "prompt": request.prompt,
                },
            }

            if enhanced_prompt and request.prompt != enhanced_prompt:
                response_data["asset_info"]["enhanced_prompt"] = enhanced_prompt

            logger.info("Image generation successful.")
            return GeneralResponse(
                status_code=200,
                data=response_data,
                message="Image generation successful",
            )
        else:
            logger.error(f"Image generation failed with status: {prediction.status}")
            return GeneralResponse(
                status_code=500,
                data=None,
                message=f"Image generation failed: {prediction.status}",
            )

    except Exception as e:
        logger.exception(f"Image generation failed: {str(e)}")
        return GeneralResponse(
            status_code=500, data=None, message=f"Image generation failed: {str(e)}"
        )
