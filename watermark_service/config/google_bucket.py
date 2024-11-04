from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

# Initialize Google Cloud Storage client and bucket
try:
    client = storage.Client()
    print("Connected to Google Cloud Storage.")

    # Replace 'your-bucket-name' with the actual name of your GCP bucket
    bucket_name = "kk-a2i-images"
    bucket = client.bucket(bucket_name)

except GoogleCloudError as e:
    print(f"An error occurred while connecting to Google Cloud Storage: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Now you can use `bucket` in your FastAPI endpoints
