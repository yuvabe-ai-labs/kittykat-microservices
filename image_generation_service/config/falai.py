import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

os.environ["FAL_KEY"] = os.getenv("FALAI_API_KEY")

fal_client = fal_client
