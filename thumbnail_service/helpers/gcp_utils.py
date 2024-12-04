from google.cloud import storage
from io import BytesIO


def upload_to_gcp(
    image_data: BytesIO, bucket_name: str, bucket_prefix: str, file_name: str
) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Combine prefix and file name for the final object path
    object_path = f"{bucket_prefix.rstrip('/')}/{file_name}"

    blob = bucket.blob(object_path)
    blob.upload_from_file(image_data, content_type="image/webp")
    blob.make_public()

    return blob.public_url
