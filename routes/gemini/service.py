import base64
from io import BytesIO
from config.env import config
from PIL import Image
from config.logger import logger
from google import genai
from google.genai.types import Content, Part
from .models import GeminiImageGenerationRequest, GeminiImageEditRequest
from core.models import ImageResponse


class GeminiService:
    def __init__(self):
        self.gemini_client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

    def generate_image(self, request: GeminiImageGenerationRequest) -> ImageResponse:
        try:
            contents = [
                Content(role="user", parts=[Part.from_text(text=request.prompt)])]

            if request.reference_images:
                for image_url in request.reference_images:
                    contents.append(Content(
                        role="user",
                        parts=[Part.inline_data(GeminiServiceUtils.convert_url_to_image_like(
                            image_url))]
                    ))

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
            )

            asset_base64s = []

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    data = part.inline_data.data
                    b64_string = base64.b64encode(data).decode('utf-8')
                    asset_base64s.append(b64_string)

            return ImageResponse(
                asset_base64s=asset_base64s,
                model_response=response.to_json_dict()
            )

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise e

    def edit_image(self, request: GeminiImageEditRequest):
        try:
            contents = [
                Content(role="user", parts=[Part.from_text(text=request.prompt)])]
            print("Added prompt part")
            contents.append(GeminiServiceUtils.convert_url_to_image_like(
                request.base_image))
            print("Added base image part")
            if request.reference_images:
                for image_url in request.reference_images:
                    contents.append(Content(
                        role="user",
                        parts=[GeminiServiceUtils.convert_url_to_image_like(
                            image_url)]

                    ))
            print(f"Added reference image part ")
            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
            )

            logger.info(f"Gemini edit image response: {response}")

            asset_base64s = []

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    data = part.inline_data.data
                    b64_string = base64.b64encode(data).decode('utf-8')
                    asset_base64s.append(b64_string)

            # Save the edited image to a file for verification
            if asset_base64s:
                with open("edited_image.png", "wb") as f:
                    f.write(base64.b64decode(asset_base64s[0]))
                logger.info("Edited image saved as edited_image.png")

            return ImageResponse(
                asset_base64s=asset_base64s,
                model_response=response.to_json_dict()
            )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise e


class GeminiServiceUtils:
    @staticmethod
    def convert_url_to_image_like(url: str) -> Image.Image:
        try:
            import requests

            response = requests.get(url)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            logger.error(f"Error converting URL to image-like object: {e}")
            raise e
