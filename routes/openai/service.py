import base64
from PIL import Image
from config.gcp import client as gcp_client
import requests
from typing import Optional
from io import BytesIO
from urllib.parse import urlparse
import os
from config.logger import logger


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
    def url_to_file_safe(url: str) -> Optional[BytesIO]:
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

            file_like = BytesIO(response.content)
            file_like.name = filename  # OpenAI uses this to determine mime type
            return file_like

        except requests.RequestException as e:
            logger.info(f"Failed to download {url}: {e}")
            return None

    def url_to_mask_file_safe(url: str) -> Optional[BytesIO]:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))

            # 1. Load your black & white mask as a grayscale image
            mask = Image.open(img).convert("L")

            # 2. Convert it to RGBA so it has space for an alpha channel
            mask_rgba = mask.convert("RGBA")

            # 3. Then use the mask itself to fill that alpha channel
            mask_rgba.putalpha(mask)

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            buf.name = "mask.png"
            return buf

        except Exception as e:
            logger.info(f"Failed to validate or convert mask image: {e}")
            return None
