import httpx
from utils.logger import logger


class GeminiServiceUtils:
    @staticmethod
    async def convert_url_to_image_bytes(url: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

                return response.content
        except Exception as e:
            logger.error(f"Error converting URL to image bytes: {e}")
            raise e
