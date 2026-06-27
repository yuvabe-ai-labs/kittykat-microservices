from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from dotenv import load_dotenv
import os

load_dotenv()

client = None
bucket = None
bucket_prefix = None

try:
    client = storage.Client()
    print("Connected to Google Cloud Storage.")
    bucket_name = "platform-img-generation-assets"
    bucket = client.bucket(bucket_name)
    bucket_prefix = os.getenv("STAGE_TYPE")

except GoogleCloudError as e:
    print(f"An error occurred while connecting to Google Cloud Storage: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
