from PIL import Image
import requests
from io import BytesIO


def resize_image(image_url: str, max_size: tuple) -> BytesIO:
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch the image from URL")

    image = Image.open(BytesIO(response.content))
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    resized_image = BytesIO()
    image.save(resized_image, format="WEBP")
    resized_image.seek(0)
    return resized_image
