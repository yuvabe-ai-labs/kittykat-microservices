import os
import base64
from io import BytesIO
from typing import Optional
from fastapi import HTTPException, UploadFile
from PIL import Image
from constants.path_constants import DEFAULT_WATERMARK_PATH, FONTS_DIR
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from config.google_bucket import bucket


def load_watermark_image(watermark_image: Optional[UploadFile]) -> Image:
    """Load the watermark image, defaulting to a pre-configured watermark if not provided."""
    if watermark_image is None:
        if not os.path.exists(DEFAULT_WATERMARK_PATH):
            raise HTTPException(
                status_code=404, detail="Default watermark image not found."
            )
        return Image.open(DEFAULT_WATERMARK_PATH).convert("RGBA")
    if not isinstance(watermark_image, UploadFile):
        raise HTTPException(status_code=400, detail="Invalid watermark file format.")

    try:
        return Image.open(watermark_image.file).convert("RGBA")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading watermark image: {str(e)}"
        )


def get_position(
    position: str, image: Image, watermark_width: int, watermark_height: int
):
    """Calculate the position to place the watermark on the original image based on the selected option."""
    positions = {
        "top_left": (0, 0),
        "top_center": ((image.width - watermark_width) // 2, 0),
        "top_right": (image.width - watermark_width, 0),
        "center_left": (0, (image.height - watermark_height) // 2),
        "center": (
            (image.width - watermark_width) // 2,
            (image.height - watermark_height) // 2,
        ),
        "center_right": (
            image.width - watermark_width,
            (image.height - watermark_height) // 2,
        ),
        "bottom_left": (0, image.height - watermark_height),
        "bottom_center": (
            (image.width - watermark_width) // 2,
            image.height - watermark_height,
        ),
        "bottom_right": (
            image.width - watermark_width,
            image.height - watermark_height,
        ),
    }
    return positions.get(position, positions["bottom_right"])


def apply_opacity(image: Image, opacity: float):
    """Apply opacity to the image."""
    alpha = image.split()[3]
    alpha = alpha.point(lambda p: int(p * (opacity / 100)))
    image.putalpha(alpha)
    return image


def encode_image_to_base64(image: Image) -> str:
    """Convert an image to base64 encoding."""
    img_bytes = BytesIO()
    image.save(img_bytes, format="WEBP")
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.getvalue()).decode("utf-8")


def upload_to_gcs(
    image: Image, folder_path: str, file_name: str, bucket_name: str, quality: int = 80
) -> str:
    """Upload the reduced version of the image to Google Cloud Storage and return the public URL."""
    try:
        # Initialize Google Cloud Storage client
        client = storage.Client()

        # Get the bucket using the bucket name provided by the user
        bucket = client.bucket(bucket_name)

        # Save the image as WEBP format with compression
        img_bytes = BytesIO()
        image.save(img_bytes, format="WEBP", quality=quality)
        img_bytes.seek(0)

        # Upload the compressed image to GCS
        compressed_blob = bucket.blob(f"{folder_path}/{file_name}")
        compressed_blob.upload_from_file(img_bytes, content_type="image/webp")

        # Return the public URL of the uploaded compressed image
        return compressed_blob.public_url

    except GoogleCloudError as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to GCS: {str(e)}")
