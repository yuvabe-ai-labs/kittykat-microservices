import base64
from io import BytesIO
from typing import Union

from config.env import config
from config.logger import logger
from core.models import ImageResponse
from google import genai
from google.genai.types import Content, Part, GenerateImagesConfig
from PIL import Image

from .models import (Gemini_2_5_Flash_Image_Preview, GeminiImageEditRequest,
                     GeminiImageGenerationRequest, Imagen4FastGenerateParams,
                     Imagen4GenerateParams, Imagen4UltraGenerateParams)


class GeminiService:
    def __init__(self):
        self.gemini_client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

    def generate_image(self, request: GeminiImageGenerationRequest) -> ImageResponse:
        try:
            match request.model:
                case "gemini-2.5-flash-image-preview":
                    return self.generate_image_with_multimodal(request)

                case "imagen-4.0-generate-001" | "imagen-4.0-ultra-generate-001" | "imagen-4.0-fast-generate-001":
                    return self.generate_image_with_imagen(request)

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

    def generate_image_with_multimodal(self, request: Union[Gemini_2_5_Flash_Image_Preview]) -> ImageResponse:
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

    def generate_image_with_imagen(self, request: Union[Imagen4FastGenerateParams,
                                                        Imagen4GenerateParams, Imagen4UltraGenerateParams]) -> ImageResponse:
        response = self.gemini_client.models.generate_images(
            model=request.model,
            prompt=request.prompt,
            config=GenerateImagesConfig(
                number_of_images=request.n,
                aspect_ratio=request.aspect_ratio,
                image_size=getattr(request, 'image_size', None)
            )
        )

        asset_base64s = []

        for image in response.generated_images:
            data = image.image.image_bytes
            b64_string = base64.b64encode(data).decode('utf-8')
            asset_base64s.append(b64_string)

        return ImageResponse(
            asset_base64s=asset_base64s,
            model_response=response.to_json_dict()
        )


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
