import base64
import uuid
from io import BytesIO

from fastapi import HTTPException
import requests
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from PIL import Image
from config.gcp import bucket_prefix, bucket, client
from config.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

stage_type = os.getenv("STAGE_TYPE")

_BUCKET_MAP = {
    "prod": "kittykat-agents",
    "stg": "kittykat-agents-stg",
    "dev": "kittykat-agents-dev",
    "beta": "kittykat-agents-beta",
}


def upload_to_gcp(source_url: str, destination_blob_name: str) -> str:
    """
    Uploads an image from a source URL to the specified GCP bucket with a prefix.
    If the image already exists, returns its public URL without re-uploading.

    Args:
        source_url (str): The URL of the image to upload.
        destination_blob_name (str): The name of the destination blob in the bucket.

    Returns:
        str: The public URL of the uploaded or existing image.
    """
    try:
        logger.info(
            "Starting upload to GCP. Source URL: %s, Destination: %s",
            source_url,
            destination_blob_name,
        )

        # Prefix the destination blob name with the bucket prefix
        full_destination_blob_name = (
            f"{bucket_prefix}/{stage_type}/{destination_blob_name}"
        )

        # Check if the blob already exists
        blob = bucket.blob(full_destination_blob_name)
        if blob.exists():
            logger.info(
                "Blob already exists in GCP. Returning public URL: %s", blob.public_url
            )
            return blob.public_url

        # Download the image from the source URL
        logger.info("Downloading image from URL: %s", source_url)
        response = requests.get(source_url)
        response.raise_for_status()  # Ensure the request was successful
        logger.info("Image downloaded successfully from URL: %s", source_url)

        # Upload the image content to the bucket
        logger.info("Uploading image to GCP bucket: %s",
                    full_destination_blob_name)
        blob.upload_from_string(response.content, content_type="image/webp")
        logger.info(
            "Image uploaded successfully to GCP bucket. Public URL: %s", blob.public_url
        )

        # Return the public URL of the uploaded file
        return blob.public_url

    except GoogleCloudError as e:
        logger.error("GCP upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"GCP upload failed: {e}")
    except Exception as e:
        logger.error("Image upload failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Image upload failed: {e}")


def upload_base64_to_gcp(base64_string: str) -> str:
    """
    Uploads a base64-encoded image to GCP and returns its public URL.
    Destination path: {stage_type}/{microservice}/{uuid}.{ext}

    Args:
        base64_string (str): Raw base64-encoded image data (no data URI prefix).
        microservice (str): The microservice name used as a path segment (e.g. "gemini").

    Returns:
        str: The public URL of the uploaded image.
    """
    try:
        file_bytes = base64.b64decode(base64_string)

        ext = "png"
        content_type = "image/png"
        try:
            image = Image.open(BytesIO(file_bytes))
            fmt = image.format.lower() if image.format else "png"
            ext = fmt
            content_type = f"image/{fmt}"
        except Exception:
            pass

        filename = f"{uuid.uuid4()}.{ext}"
        blob_name = f"microservice/{filename}"

        size_bytes = len(file_bytes)
        metadata = {
            "file-type": content_type,
            "size": str(size_bytes),
        }

        try:
            width, height = image.size
            metadata["width"] = str(width)
            metadata["height"] = str(height)
        except Exception:
            pass

        gemini_bucket_name = _BUCKET_MAP.get(stage_type, "kittykat-agents-dev")
        gemini_bucket = client.bucket(gemini_bucket_name)

        blob = gemini_bucket.blob(blob_name)
        blob.metadata = metadata
        blob.upload_from_string(file_bytes, content_type=content_type)

        logger.info("Base64 image uploaded to GCS: %s", blob.public_url)
        return blob.public_url

    except GoogleCloudError as e:
        logger.error("GCP base64 upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"GCP upload failed: {e}")
    except Exception as e:
        logger.error("Base64 image upload failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Image upload failed: {e}")
