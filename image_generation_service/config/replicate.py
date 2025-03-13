import os
from fastapi import HTTPException
import httpx
import replicate
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("REPLICATE_API_KEY")

client = replicate.Client(api_token=api_key)

REPLICATE_API_BASE_URL = "https://api.replicate.com/v1"


async def get_api_client():
    """Get a client for the Replicate API with auth token."""
    if not api_key:
        raise HTTPException(
            status_code=500, detail="REPLICATE_API_TOKEN not configured"
        )

    client = httpx.AsyncClient(
        base_url=REPLICATE_API_BASE_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0,
    )
    try:
        yield client
    finally:
        await client.aclose()
