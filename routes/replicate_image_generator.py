from fastapi import APIRouter, HTTPException
from config.replicate import client
from models.global_models import GeneralResponse
from models.replicate_models import ImageRequest

router = APIRouter()


@router.post("/replicate/image/generate", response_model=GeneralResponse)
async def generate_image(request: ImageRequest):
    """
    Generate an image based on the provided prompt using the Replicate API.

    Args:
        request (ImageRequest): A request object containing the prompt.

    Returns:
        GeneralResponse: A response object with the status code, data, and message.
    """
    try:
        image = client.run(
            "black-forest-labs/flux-dev", input={"prompt": request.prompt}
        )
        return GeneralResponse(
            status_code=200,
            data={"image_url": image[0].url},
            message="Image generation successful",
        )
    except Exception as e:
        return GeneralResponse(
            status_code=500, data=None, message=f"Image generation failed: {str(e)}"
        )
