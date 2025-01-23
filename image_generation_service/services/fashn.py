import httpx
from models.fashn_models import (
    RunPredictionRequest,
    RunPredictionResponse,
    PredictionStatus,
)

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("FASHN_API_KEY")


class FashnService:
    BASE_URL = "https://api.fashn.ai/v1"

    def __init__(self):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def run_prediction(self, request: RunPredictionRequest) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/run", headers=self.headers, json=request.dict()
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]

    async def get_prediction_status(self, prediction_id: str) -> PredictionStatus:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/status/{prediction_id}", headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return PredictionStatus(**data)
