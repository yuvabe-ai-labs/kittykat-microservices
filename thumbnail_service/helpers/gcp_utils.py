from google.cloud import storage
from io import BytesIO


def upload_to_gcp(
    image_data: BytesIO, bucket_name: str, bucket_prefix: str, file_name: str
) -> str:
    # Create a client for interacting with Google Cloud Storage
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Combine prefix and file name for the final object path
    object_path = f"{bucket_prefix.rstrip('/')}/{file_name}"

    # Upload the image data to the specified GCP bucket
    blob = bucket.blob(object_path)
    blob.upload_from_file(image_data, content_type="image/webp")

    # Instead of make_public, ensure proper IAM permissions are set for the bucket

    # Return the public URL, assuming appropriate IAM policies for public access
    return blob.public_url
