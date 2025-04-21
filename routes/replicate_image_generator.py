import os
import uuid
from fastapi import APIRouter
from openai import OpenAI
from services.gcp import upload_to_gcp
from models.global_models import GeneralResponse
from models.replicate_models import ImageRequest
from services.enhance_prompt import enhance_prompt
from services.replicate import generate_prediction
from config.logger import logger
from datetime import datetime, timezone
from .replicate.predictions.models import CreatePredictionRequest
from .replicate.predictions.router import create_prediction

router = APIRouter()

from dotenv import load_dotenv

load_dotenv()


async def generate_with_dalle(prompt: str) -> dict:
    """Generate an image using OpenAI's DALL-E model."""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model="dall-e-3",  # Can be parameterized in the future
            prompt=prompt,
            size="1024x1024",  # Can be parameterized in the future
            quality="hd",
            n=1,
        )

        # Extract the URL from the response
        image_url = response.data[0].url
        image_id = f"dalle_{os.urandom(8).hex()}"

        return {
            "status": "succeeded",
            "output": image_url,
            "model": "dall-e-3",
            "created_at": None,  # OpenAI doesn't provide these timestamps
            "started_at": None,
            "completed_at": None,
            "metrics": {},
            "id": image_id,  # Always use our generated ID
        }
    except Exception as e:
        logger.exception(f"DALL-E image generation failed: {str(e)}")
        raise e


@router.post("/replicate/image/generate", response_model=GeneralResponse)
async def generate_image(request: ImageRequest):
    """
    Generate an image based on the provided prompt using either Replicate API or OpenAI DALL-E,
    then upload to GCP. If enhance_prompt is True, the prompt is first enhanced.
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
                    message=f"Prompt enhancement failed: {str(e)}",
                )

        # Generate image based on the provider
        if request.provider.lower() == "openai":
            logger.info("Using OpenAI DALL-E for image generation...")
            try:
                prediction_data = await generate_with_dalle(enhanced_prompt)
            except Exception as e:
                return GeneralResponse(
                    status_code=500,
                    data=None,
                    message=f"OpenAI image generation failed: {str(e)}",
                )
        else:  # Default to replicate
            logger.info("Using Replicate for image generation...")
            # Create a prediction request
            prediction_request = CreatePredictionRequest(
                version=request.model, input={"prompt": enhanced_prompt}
            )

            # Call the create_prediction endpoint with prefer: wait header
            logger.info("Creating prediction with wait preference...")
            prediction_response = await create_prediction(
                request=prediction_request,
                prefer="wait",  # Wait for up to 300 seconds for the prediction to complete
            )

            # Handle the prediction response
            if prediction_response.status_code != 200:
                logger.error(
                    f"Prediction failed with status: {prediction_response.status_code}"
                )
                return GeneralResponse(
                    status_code=prediction_response.status_code,
                    data=None,
                    message=f"Image generation failed: {prediction_response.message}",
                )

            prediction_data = prediction_response.data

        # Upload the image to GCP
        if prediction_data["status"] == "succeeded":
            logger.info("Prediction succeeded, uploading to GCP...")

            # Handle different model output formats
            image_url = None
            if (
                isinstance(prediction_data["output"], list)
                and len(prediction_data["output"]) > 0
            ):
                image_url = prediction_data["output"][0]
            elif isinstance(prediction_data["output"], str):
                image_url = prediction_data["output"]

            if not image_url:
                return GeneralResponse(
                    status_code=500, data=None, message="No image output from model"
                )

            # Generate a unique filename
            unique_id = prediction_data.get("id", f"img_{os.urandom(8).hex()}")
            gcp_url = upload_to_gcp(
                image_url,
                f"{'openai' if request.provider.lower() == 'openai' else 'replicate'}_outputs/{unique_id}.webp",
            )

            response_data = {
                "asset_url": gcp_url,
                "asset_info": {
                    "model": prediction_data.get("model", request.model),
                    "created_at": prediction_data.get("created_at"),
                    "started_at": prediction_data.get("started_at"),
                    "completed_at": prediction_data.get("completed_at"),
                    "status": prediction_data.get("status"),
                    "metrics": prediction_data.get("metrics", {}),
                    "prompt": request.prompt,
                    "provider": request.provider,
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
                f"Image generation failed with status: {prediction_data.get('status', 'unknown')}"
            )
            return GeneralResponse(
                status_code=500,
                data=None,
                message=f"Image generation failed: {prediction_data.get('status', 'unknown')}",
            )

    except Exception as e:
        logger.exception(f"Image generation failed: {str(e)}")
        return GeneralResponse(
            status_code=500, data=None, message=f"Image generation failed: {str(e)}"
        )
