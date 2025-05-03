import httpx
from dotenv import load_dotenv
import os
from models.video_generation_model import RunPredictionRequest, PredictionStatus

load_dotenv()

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
# MODEL_NAME = "kwaivgi/kling-v1.6-standard"


class ReplicateService:
    BASE_URL = "https://api.replicate.com/v1"

    def __init__(self):
        self.headers = {
            "Authorization": f"Token {REPLICATE_API_KEY}",
            "Content-Type": "application/json",
        }

    async def create_prediction(self, request: RunPredictionRequest) -> str:

        # input_data = {"prompt": request.prompt}

        # # Include start_image only if provided
        # if request.start_image:
        #     input_data["start_image"] = request.start_image

        # input_data.update({
        #     "duration": request.duration,
        #     "aspect_ratio": request.aspect_ratio,
        #     "cfg_scale": request.cfg_scale,
        #     "negative_prompt": request.negative_prompt
        # })

        model_name = "kwaivgi/kling-v1.6-pro" if request.end_image else "kwaivgi/kling-v1.6-standard"
        print(f"Using model: {model_name}")


        input_data = {
            "prompt": request.prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "cfg_scale": request.cfg_scale,
            "negative_prompt": request.negative_prompt
        }

        # Include start and end images only if provided
        if request.start_image:
            input_data["start_image"] = request.start_image
        if request.end_image:
            input_data["end_image"] = request.end_image

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/models/{model_name}/predictions",
                headers=self.headers,
                json={"input": input_data},
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]

    async def get_prediction_status(self, prediction_id: str) -> PredictionStatus:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/predictions/{prediction_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()
            print("data inside service",data)
            return PredictionStatus(**data)

    async def cancel_prediction(self, prediction_id: str) -> dict:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/predictions/{prediction_id}/cancel",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def list_all_predictions(self) -> list:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/predictions",
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
