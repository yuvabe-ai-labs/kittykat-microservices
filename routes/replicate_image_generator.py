import uuid
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
            prediction_output = generate_prediction(request.model, enhanced_prompt)
        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            return GeneralResponse(
                status_code=500,
                data=None,
                message=str(e),
            )

        # If the model is the specified one, it returns a direct URL
        if (
            request.model
            == "kittykat-ai/swyft:b819072f68811372560fe983c7fbc7921a2386d9a42cb1e35c203fb62799014e"
        ):
            logger.info("Direct model detected, uploading to GCP...")
            gcp_url = upload_to_gcp(
                prediction_output, f"replicate_outputs/{uuid.uuid4()}.webp"
            )
            response_data = {
                "asset_url": gcp_url,
                "asset_info": {
                    "model": request.model,
                    "prompt": request.prompt,
                },
            }
            if enhanced_prompt and request.prompt != enhanced_prompt:
                response_data["asset_info"]["enhanced_prompt"] = enhanced_prompt

            return GeneralResponse(
                status_code=200,
                data=response_data,
                message="Image generation successful",
            )

        # Handle prediction result for other models
        if prediction_output.status == "succeeded":
            logger.info("Prediction succeeded, uploading to GCP...")
            gcp_url = upload_to_gcp(
                prediction_output.output[0],
                f"replicate_outputs/{prediction_output.id}.webp",
            )

            response_data = {
                "asset_url": gcp_url,
                "asset_info": {
                    "model": prediction_output.model,
                    "created_at": prediction_output.created_at,
                    "started_at": prediction_output.started_at,
                    "completed_at": prediction_output.completed_at,
                    "status": prediction_output.status,
                    "metrics": prediction_output.metrics,
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
            logger.error(
                f"Image generation failed with status: {prediction_output.status}"
            )
            return GeneralResponse(
                status_code=500,
                data=None,
                message=f"Image generation failed: {prediction_output.status}",
            )

    except Exception as e:
        logger.exception(f"Image generation failed: {str(e)}")
        return GeneralResponse(
            status_code=500, data=None, message=f"Image generation failed: {str(e)}"
        )
