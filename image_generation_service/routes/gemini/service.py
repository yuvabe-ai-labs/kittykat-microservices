import base64
from io import BytesIO
from typing import Union

from config.env import config
from config.logger import logger
from core.models import ImageResponse
from google import genai
from google.genai.types import Content, Part, GenerateImagesConfig, GenerateContentConfig
from PIL import Image

from .constants import VIRTUAL_TRY_ON_BASE_PROMPT
from .models import (Gemini_2_5_Flash_Image_Preview, GeminiImageEditRequest,
                     GeminiImageGenerationRequest, Imagen4FastGenerateParams,
                     Imagen4GenerateParams, Imagen4UltraGenerateParams, GeminiVirtualTryOnRequest)


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

            if request.reference_images:
                for image_url in request.reference_images:
                    contents.append(GeminiServiceUtils.convert_url_to_image_like(
                        image_url))

            contents.append(GeminiServiceUtils.convert_url_to_image_like(
                request.base_image))

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=['Image']
                )
            )

            asset_base64s = []

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        b64_string = base64.b64encode(data).decode('utf-8')
                        asset_base64s.append(b64_string)

            if not asset_base64s:
                logger.info(response.sdk_http_response)
                # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
                return ImageResponse(
                    error=response.to_json_dict(),
                    is_nsfw_detected=True,
                    model_usage=response.usage_metadata
                )

            return ImageResponse(
                asset_base64s=asset_base64s,
                model_response=response.to_json_dict(),
                model_usage=response.usage_metadata
            )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise e

    def generate_vton_image(self, request: GeminiVirtualTryOnRequest) -> ImageResponse:
        try:
            prompt = VIRTUAL_TRY_ON_BASE_PROMPT

            if request.prompt:
                prompt += f"Additional instructions: {request.prompt}"

            contents = [
                Content(role="user", parts=[Part.from_text(text=prompt)])]
            contents.append(GeminiServiceUtils.convert_url_to_image_like(
                request.product_image))
            contents.append(GeminiServiceUtils.convert_url_to_image_like(
                request.model_image))

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=['Image']
                )
            )

            asset_base64s = []

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        b64_string = base64.b64encode(data).decode('utf-8')
                        asset_base64s.append(b64_string)

            if not asset_base64s:
                logger.info(response.sdk_http_response)
                # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
                return ImageResponse(
                    error=response.to_json_dict(),
                    is_nsfw_detected=True,
                    model_usage=response.usage_metadata
                )

            return ImageResponse(
                asset_base64s=asset_base64s,
                model_response=response.to_json_dict(),
                model_usage=response.usage_metadata
            )

        except Exception as e:
            logger.error(f"Error generating virtual try-on image: {e}")
            raise e

    def generate_image_with_multimodal(self, request: Union[Gemini_2_5_Flash_Image_Preview]) -> ImageResponse:
        contents = [
            Content(role="user", parts=[Part.from_text(text=request.prompt)])]

        if request.reference_images:
            for image_url in request.reference_images:
                contents.append(
                    GeminiServiceUtils.convert_url_to_image_like(image_url))

        response = self.gemini_client.models.generate_content(
            model=request.model,
            contents=contents,
            config=GenerateContentConfig(
                response_modalities=['Image']
            )
        )

        asset_base64s = []

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    data = part.inline_data.data
                    b64_string = base64.b64encode(data).decode('utf-8')
                    asset_base64s.append(b64_string)

        if not asset_base64s:
            logger.info(response.sdk_http_response)
            # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
            return ImageResponse(
                error=response.to_json_dict(),
                is_nsfw_detected=True,
                model_usage=response.usage_metadata
            )

        return ImageResponse(
            asset_base64s=asset_base64s,
            model_response=response.to_json_dict(),
            model_usage=response.usage_metadata
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

        if not response.generated_images:
            logger.info(response.sdk_http_response)
            # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
            return ImageResponse(
                error=response.to_json_dict(),
                is_nsfw_detected=True,
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
