import base64
from config.gcp import client as gcp_client


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
            print(f"Error uploading image to bucket: {e}")
            raise e
