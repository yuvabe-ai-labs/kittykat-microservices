import httpx
from models.fashn_models import (
    RunPredictionRequest,
    RunPredictionResponse,
    PredictionStatus,
)

from dotenv import load_dotenv
import os
from config.logger import logger

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
        try:
            logger.debug(
                f"Sending prediction request to FASHN API: {request.dict(exclude_none=True)}"
            )
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.BASE_URL}/run",
                    headers=self.headers,
                    json=request.dict(exclude_none=True),
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Received response from FASHN API: {data}")
                return data["id"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from FASHN API: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error during FASHN API prediction request: {str(e)}")
            raise

    async def get_prediction_status(self, prediction_id: str) -> PredictionStatus:
        try:
            logger.debug(f"Fetching status for prediction ID: {prediction_id}")
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    f"{self.BASE_URL}/status/{prediction_id}", headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Received status response from FASHN API: {data}")
                return PredictionStatus(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error from FASHN API status endpoint: {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Error fetching prediction status: {str(e)}")
            raise
