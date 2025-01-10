import os
import replicate
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("REPLICATE_API_KEY")

client = replicate.Client(api_token=api_key)
