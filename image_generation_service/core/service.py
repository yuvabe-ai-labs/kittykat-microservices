import base64
import requests
from typing import Optional

from config.logger import logger
from PIL import Image


class ImageUtilsService:
    @staticmethod
    def convert_url_to_base64(url: str, raise_exception: bool = True):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Convert bytes → base64 string
            b64_string = base64.b64encode(response.content).decode("utf-8")
            return b64_string

        except Exception as e:
            logger.error(f"Error converting URL to base64: {e}")
            if raise_exception:
                raise e

            return None
