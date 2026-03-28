import base64
import json
from typing import List, Union
from urllib.parse import unquote

from google.oauth2 import service_account
from config.env import config
from config.logger import logger
from core.models import ImageResponse
from google import genai
from google.genai.types import (
    Content,
    Part,
    GenerateImagesConfig,
    GenerateContentConfig,
    ImageConfig,
)
from services.gcp import upload_base64_to_gcp

from utils.helpers import safe_log_dict, gemini_retry


from .constants import VIRTUAL_TRY_ON_BASE_PROMPT
from .models import (
    Gemini_2_5_Flash_Image_Preview,
    GeminiImageEditRequest,
    GeminiImageGenerationRequest,
    Imagen4FastGenerateParams,
    Imagen4GenerateParams,
    Imagen4UltraGenerateParams,
    GeminiVirtualTryOnRequest,
    NanoBananaPro,
    NanoBanana2,
    NanoBanana2Edit,
)


class GeminiService:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)

    @staticmethod
    def _upload_base64s(base64_list: List[str]) -> List[str]:
        urls = []
        for b64 in base64_list:
            url = upload_base64_to_gcp(b64)
            urls.append(url)
        return urls

    def generate_image(self, request: GeminiImageGenerationRequest) -> ImageResponse:
        logger.info(f"Generating image with model: {request.model}")
        try:
            match request.model:
                case (
                    "gemini-2.5-flash-image"
                    | "gemini-2.5-flash-image-preview"
                    | "gemini-3-pro-image-preview"
                    | "gemini-3.1-flash-image-preview"
                ):
                    return self.generate_image_with_multimodal(request)

                case (
                    "imagen-4.0-generate-001"
                    | "imagen-4.0-ultra-generate-001"
                    | "imagen-4.0-fast-generate-001"
                ):
                    return self.generate_image_with_imagen(request)

        except Exception as e:
            logger.error(f"Error generating image with model {request.model}: {e}")
            raise e

    @gemini_retry
    def edit_image(self, request: GeminiImageEditRequest):
        logger.info(f"Editing image with model: {request.model}")
        try:
            contents = [
                Content(role="user", parts=[Part.from_text(text=request.prompt)])
            ]

            image_uris = list(request.reference_images or []) + [request.base_image]
            registered = GeminiServiceUtils.register_gcs_files(image_uris)
            contents.extend(registered)

            aspect_ratio = (
                request.aspect_ratio
                if (hasattr(request, "aspect_ratio") and request.aspect_ratio != "auto")
                else None
            )
            resolution = request.resolution if hasattr(request, "resolution") else None

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution,
                    ),
                ),
            )

            asset_base64s = []

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        b64_string = base64.b64encode(data).decode("utf-8")
                        asset_base64s.append(b64_string)

            logger.info(f"Asset base64s length: {len(asset_base64s)}")

            if not asset_base64s:
                # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
                return ImageResponse(
                    error=response.to_json_dict(),
                    is_nsfw_detected=True,
                    model_usage=response.usage_metadata,
                )

            logger.info(f"Edited image successfully with model {request.model}")

            asset_urls = self._upload_base64s(asset_base64s)
            return ImageResponse(
                asset_urls=asset_urls,
                model_response=safe_log_dict(response.to_json_dict()),
                model_usage=response.usage_metadata,
            )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise e

    @gemini_retry
    def generate_vton_image(self, request: GeminiVirtualTryOnRequest) -> ImageResponse:
        logger.info(f"Generating virtual try-on image with model: {request.model}")
        try:
            prompt = VIRTUAL_TRY_ON_BASE_PROMPT

            if request.prompt:
                logger.info("Appending additional user instructions to VTON prompt")
                prompt += f"Additional instructions: {request.prompt}"

            contents = [Content(role="user", parts=[Part.from_text(text=prompt)])]
            registered = GeminiServiceUtils.register_gcs_files(
                [request.product_image, request.model_image]
            )
            contents.extend(registered)

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
                config=GenerateContentConfig(response_modalities=["Image"]),
            )

            asset_base64s = []

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        b64_string = base64.b64encode(data).decode("utf-8")
                        asset_base64s.append(b64_string)

            if not asset_base64s:
                logger.warning(
                    f"VTON response returned no images, possible NSFW content. HTTP response: {response.sdk_http_response}"
                )
                # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
                return ImageResponse(
                    error=response.to_json_dict(),
                    is_nsfw_detected=True,
                    model_usage=response.usage_metadata,
                )

            logger.info(
                f"Virtual try-on image generated successfully with model {request.model}"
            )
            asset_urls = self._upload_base64s(asset_base64s)
            return ImageResponse(
                asset_urls=asset_urls,
                model_response=safe_log_dict(response.to_json_dict()),
                model_usage=response.usage_metadata,
            )

        except Exception as e:
            logger.error(
                f"Error generating virtual try-on image with model {request.model}: {e}"
            )
            raise e

    @gemini_retry
    def generate_image_with_multimodal(
        self, request: Union[Gemini_2_5_Flash_Image_Preview, NanoBananaPro, NanoBanana2]
    ) -> ImageResponse:
        logger.info(
            f"Generating image via multimodal with model: {request.model}, aspect_ratio: {request.aspect_ratio}"
        )

        try:
            contents = [
                Content(role="user", parts=[Part.from_text(text=request.prompt)])
            ]

            if request.reference_images:
                registered = GeminiServiceUtils.register_gcs_files(
                    list(request.reference_images)
                )
                contents.extend(registered)

            response = self.gemini_client.models.generate_content(
                model=request.model,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=ImageConfig(
                        aspect_ratio=(
                            None
                            if request.aspect_ratio == "auto"
                            else request.aspect_ratio
                        ),
                        image_size=(
                            request.resolution
                            if hasattr(request, "resolution")
                            else None
                        ),
                    ),
                ),
            )

            asset_base64s = []

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        b64_string = base64.b64encode(data).decode("utf-8")
                        asset_base64s.append(b64_string)

            if not asset_base64s:
                logger.warning(
                    f"Multimodal response returned no images, possible NSFW content. HTTP response: {response.sdk_http_response}"
                )
                # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
                return ImageResponse(
                    error=response.to_json_dict(),
                    is_nsfw_detected=True,
                    model_usage=response.usage_metadata,
                )

            logger.info(
                f"Image generated successfully via multimodal with model {request.model}, images: {len(asset_base64s)}"
            )
            asset_urls = self._upload_base64s(asset_base64s)
            image_response = ImageResponse(
                asset_urls=asset_urls,
                model_response=safe_log_dict(response.to_json_dict()),
                model_usage=response.usage_metadata,
            )
            self._log_multimodal_response(image_response)
            return image_response

        except Exception as e:
            logger.error(
                f"Error generating image via multimodal with model {request.model}: {e}"
            )
            raise e

    @staticmethod
    def _log_multimodal_response(image_response: ImageResponse) -> None:
        model_response = image_response.model_response or {}
        usage = model_response.get("usage_metadata") or {}
        candidates = model_response.get("candidates") or []

        log_data = {
            "is_nsfw_detected": image_response.is_nsfw_detected,
            "error": image_response.error,
            "images_count": (
                len(image_response.asset_urls) if image_response.asset_urls else 0
            ),
            "model_version": model_response.get("model_version"),
            "response_id": model_response.get("response_id"),
            "finish_reason": candidates[0].get("finish_reason") if candidates else None,
            "usage": {
                "total_token_count": usage.get("total_token_count"),
                "prompt_token_count": usage.get("prompt_token_count"),
                "candidates_token_count": usage.get("candidates_token_count"),
                "thoughts_token_count": usage.get("thoughts_token_count"),
            },
        }
        logger.info(f"Multimodal image response:\n{json.dumps(log_data, indent=2)}")

    @gemini_retry
    def generate_image_with_imagen(
        self,
        request: Union[
            Imagen4FastGenerateParams, Imagen4GenerateParams, Imagen4UltraGenerateParams
        ],
    ) -> ImageResponse:
        logger.info(
            f"Generating image via Imagen with model: {request.model}, n: {request.n}, aspect_ratio: {request.aspect_ratio}"
        )
        response = self.gemini_client.models.generate_images(
            model=request.model,
            prompt=request.prompt,
            config=GenerateImagesConfig(
                number_of_images=request.n,
                aspect_ratio=request.aspect_ratio,
                image_size=getattr(request, "image_size", None),
            ),
        )

        if not response.generated_images:
            logger.warning(
                f"Imagen response returned no images, possible NSFW content. HTTP response: {response.sdk_http_response}"
            )
            # Since there is no official documentation on how NSFW content is handled, we assume that an empty response indicates NSFW content.
            return ImageResponse(
                error=response.to_json_dict(),
                is_nsfw_detected=True,
            )

        asset_base64s = []

        for image in response.generated_images:
            data = image.image.image_bytes
            b64_string = base64.b64encode(data).decode("utf-8")
            asset_base64s.append(b64_string)

        logger.info(
            f"Image generated successfully via Imagen with model {request.model}, images: {len(asset_base64s)}"
        )
        asset_urls = self._upload_base64s(asset_base64s)
        return ImageResponse(
            asset_urls=asset_urls,
            model_response=safe_log_dict(response.to_json_dict()),
        )


class GeminiServiceUtils:
    _oauth_client: genai.Client = None
    _gcs_creds: service_account.Credentials = None

    @classmethod
    def _get_oauth_client(cls) -> tuple[genai.Client, service_account.Credentials]:
        if cls._oauth_client is None:
            sa_info = json.loads(
                base64.b64decode(config.BUCKET_SA_KEY).decode("utf-8")
            )
            cls._gcs_creds = service_account.Credentials.from_service_account_info(
                sa_info,
                scopes=[
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/devstorage.read_only",
                ],
            ).with_quota_project(sa_info["project_id"])
            cls._oauth_client = genai.Client(credentials=cls._gcs_creds)
        return cls._oauth_client, cls._gcs_creds

    @staticmethod
    def to_gcs_uri(url: str) -> str:
        if url.startswith("gs://"):
            return url
        if "storage.googleapis.com/" in url:
            path = url.split("storage.googleapis.com/", 1)[1].split("?")[0]
            return f"gs://{unquote(path)}"
        return url

    @classmethod
    def register_gcs_files(cls, uris: List[str]) -> list:
        oauth_client, creds = cls._get_oauth_client()
        gcs_uris = [cls.to_gcs_uri(u) for u in uris]
        logger.info(f"Registering {len(gcs_uris)} GCS file(s): {gcs_uris}")
        result = oauth_client.files.register_files(uris=gcs_uris, auth=creds)
        return result.files
