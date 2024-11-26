import aiohttp
from PIL import Image
import io
from typing import Tuple

async def check_image_dimensions(url: str) -> Tuple[bool, str]:
    """
    Check if the image dimensions are at least 224x224 pixels.
    Args:
        url (str): The URL of the image to check.
    Returns:
        Tuple[bool, str]: A tuple where the first value indicates if the dimensions are valid,
                          and the second value provides a message.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, f"Failed to fetch image from URL, status code: {response.status}"

                image_data = await response.read()
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size

                if width < 224 or height < 224:
                    return False, "Image dimensions are below 224x224 pixels. Ensure the image meets the minimum size requirement."

                return True, "Image dimensions are valid."
        except Exception as e:
            return False, f"Error processing the image: {str(e)}"
