from fastapi import HTTPException
import requests
from google.cloud.exceptions import GoogleCloudError


def upload_to_gcp(bucket, source_url, destination_blob_name):
    """
    Uploads an image from a source URL to the specified bucket.
    """
    try:
        # Download the image from the source URL
        response = requests.get(source_url)
        response.raise_for_status()  # Ensure the request was successful

        # Create a blob in the bucket and upload the content
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(response.content, content_type="image/webp")

        # Return the public URL of the uploaded file
        return f"https://storage.googleapis.com/{bucket.name}/{destination_blob_name}"
    except GoogleCloudError as e:
        raise HTTPException(status_code=500, detail=f"GCP upload failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")
