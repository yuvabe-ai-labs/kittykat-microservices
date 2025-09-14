from utils.logger import logger
from io import BytesIO
from PIL import Image


class GeminiServiceUtils:
    @staticmethod
    def convert_url_to_image_like(url: str) -> Image.Image:
        try:
            import requests

            response = requests.get(url)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            logger.error(f"Error converting URL to image-like object: {e}")
            raise e
