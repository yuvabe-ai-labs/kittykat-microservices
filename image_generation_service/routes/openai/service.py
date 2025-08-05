import base64
from PIL import Image, ImageOps
from config.gcp import client as gcp_client
import requests
from typing import Optional
from io import BytesIO
from urllib.parse import urlparse
import os
from config.logger import logger
from .config import client


class ImageService:
    @staticmethod
    def upload_base64_image_to_bucket(image_base64: str, bucket_name: str, prefix: str, type: str) -> str:
        try:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(image_base64)

            # Get the bucket
            bucket = gcp_client.bucket(bucket_name)

            # Create a blob and upload the image
            blob = bucket.blob(prefix)
            blob.upload_from_string(image_bytes, content_type=f"image/{type}")

            # Return the public URL
            return blob.public_url

        except Exception as e:
            logger.info(f"Error uploading image to bucket: {e}")
            raise e

    @staticmethod
    def url_to_file_safe(url: str):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Try to extract filename from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                # Default to a PNG file if extension is missing
                filename = "file.png"

            # Validate supported extensions
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".png", ".jpeg", ".webp"]:
                logger.info(
                    f"Unsupported extension: {ext}. Defaulting to .png")
                filename = "file.png"

            file_content_type = response.headers.get(
                "Content-Type", "").lower()
            if file_content_type not in ["image/png", "image/jpeg", "image/webp"]:
                logger.warning(
                    f"Invalid or missing content-type: {file_content_type}. Forcing image/png"
                )
                file_content_type = "image/png"

            file_content = BytesIO(response.content)
            file = (
                filename,
                file_content,
                file_content_type
            )
            return file

        except requests.RequestException as e:
            logger.info(f"Failed to download {url}: {e}")
            return None

    @staticmethod
    def url_to_mask_file_safe(url: str) -> Optional[BytesIO]:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))

            # 1. Load your black & white mask as a grayscale image
            mask = img.convert("L")

            mask_inverted = ImageOps.invert(mask)

            # 2. Convert it to RGBA so it has space for an alpha channel
            mask_rgba = mask_inverted.convert("RGBA")

            # 3. Then use the mask itself to fill that alpha channel
            mask_rgba.putalpha(mask_inverted)

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            buf.name = "mask.png"
            return buf

        except Exception as e:
            logger.info(f"Failed to validate or convert mask image: {e}")
            return None

    @staticmethod
    def create_lifestyle_image(
        reference_image: str,
        model_image: str
    ) -> str:
        try:

            image_files = []
            reference_image = ImageService.url_to_file_safe(reference_image)
            model_image = ImageService.url_to_file_safe(model_image)

            if reference_image is None or model_image is None:
                raise ValueError(
                    "One or both images could not be downloaded or are invalid.")

            image_files.append(model_image)
            image_files.append(reference_image)

            result = client.images.edit(
                model="gpt-image-1",
                size="1024x1024",
                background="auto",
                quality="high",
                n=1,
                prompt="Generate a lifestyle scene inspired by the reference image, seamlessly integrating the provided model image.",
                image=image_files
            )

            if not result.data or not result.data[0].b64_json:
                raise Exception("No image data returned from OpenAI API")

            image_base64 = result.data[0].b64_json

            logger.info("Lifestyle image created successfully.")

            return image_base64

        except Exception as e:
            logger.info(f"Failed to create lifestyle image: {e}")
            raise e
