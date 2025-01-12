from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

try:
    client = storage.Client()
    print("Connected to Google Cloud Storage.")
    bucket_name = "platform-thumb-img-assets"
    bucket = client.bucket(bucket_name)

except GoogleCloudError as e:
    print(f"An error occurred while connecting to Google Cloud Storage: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
