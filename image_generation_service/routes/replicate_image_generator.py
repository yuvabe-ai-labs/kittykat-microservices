import time
from fastapi import APIRouter, HTTPException
from config.replicate import client
from services.gcp import upload_to_gcp
from models.global_models import GeneralResponse
from models.replicate_models import ImageRequest
from config.gcp import bucket

router = APIRouter()


@router.post("/replicate/image/generate", response_model=GeneralResponse)
async def generate_image(request: ImageRequest):
    """
    Generate an image based on the provided prompt using the Replicate API and upload to GCP.
    """
    try:
        # Create prediction using Replicate API
        prediction = client.predictions.create(
            model="black-forest-labs/flux-dev", input={"prompt": request.prompt}
        )

        # Poll for completion
        while prediction.status not in ["succeeded", "failed", "canceled"]:
            time.sleep(2)
            prediction = client.predictions.get(prediction.id)

        # Check the prediction result
        if prediction.status == "succeeded":
            # Use the initialized bucket directly
            gcp_url = upload_to_gcp(
                bucket,  # The initialized bucket object
                prediction.output[0],  # Replicate output URL
                f"generated-images/{prediction.id}.webp",  # Destination path in bucket
            )

            return GeneralResponse(
                status_code=200,
                data={
                    "asset_url": gcp_url,  # GCP URL
                    "asset_info": {
                        "model": prediction.model,
                        "created_at": prediction.created_at,
                        "started_at": prediction.started_at,
                        "completed_at": prediction.completed_at,
                        "status": prediction.status,
                        "metrics": prediction.metrics,
                    },
                },
                message="Image generation successful",
            )

        else:
            return GeneralResponse(
                status_code=500,
                data=None,
                message=f"Image generation failed: {prediction.status}",
            )
    except Exception as e:
        return GeneralResponse(
            status_code=500, data=None, message=f"Image generation failed: {str(e)}"
        )
