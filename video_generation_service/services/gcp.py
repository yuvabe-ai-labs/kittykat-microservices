from fastapi import HTTPException
import requests
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from config.gcp import bucket_prefix, bucket
from config.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

stage_type = os.getenv("STAGE_TYPE")

def upload_video_to_gcp(source_url: str, destination_blob_name: str) -> str:
    """
    Uploads a video from a source URL to the specified GCP bucket with a prefix.
    If the video already exists, returns its public URL without re-uploading.

    Args:
        source_url (str): The URL of the video to upload.
        destination_blob_name (str): The name of the destination blob in the bucket.

    Returns:
        str: The public URL of the uploaded or existing video.
    """
    try:
        logger.info(
            "Starting upload to GCP. Source URL: %s, Destination: %s",
            source_url,
            destination_blob_name,
        )

        # Prefix the destination blob name with the bucket prefix
        full_destination_blob_name = (
            f"{stage_type}/{destination_blob_name}"
        )

        # Check if the blob already exists
        blob = bucket.blob(full_destination_blob_name)
        if blob.exists():
            logger.info(
                "Blob already exists in GCP. Returning public URL: %s", blob.public_url
            )
            return blob.public_url

        # Download the video from the source URL
        logger.info("Downloading video from URL: %s", source_url)
        response = requests.get(source_url, stream=True)
        response.raise_for_status()  # Ensure the request was successful
        logger.info("Video downloaded successfully from URL: %s", source_url)

        # Upload the video content to the bucket
        logger.info("Uploading video to GCP bucket: %s", full_destination_blob_name)
        blob.upload_from_string(response.content, content_type="video/mp4")
        logger.info(
            "Video uploaded successfully to GCP bucket. Public URL: %s", blob.public_url
        )

        # Return the public URL of the uploaded file
        return blob.public_url

    except GoogleCloudError as e:
        logger.error("GCP upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"GCP upload failed: {e}")
    except Exception as e:
        logger.error("Video upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video upload failed: {e}")
