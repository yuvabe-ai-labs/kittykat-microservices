from pydantic import HttpUrl
import aiohttp
from config.logger import logger


async def enhance_prompt(prompt: str) -> str:
    """
    Enhance the given prompt using the OpenAI enhancement service.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://platform-openai-wrapper-service-dev-547175224231.us-central1.run.app/prompt/enhance",
                json={"prompt": prompt},
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("data", {}).get("enhanced_prompt", prompt)
                else:
                    raise Exception(f"HTTP {response.status}: Failed to enhance prompt")
    except Exception as e:
        raise Exception(f"Failed to enhance prompt: {str(e)}")


async def image_to_description(
    image_url: HttpUrl, user_prompt: str, focus_entitiy: str, trigger_word: str
) -> str:
    """Enhance the given prompt using OpenAI service."""
    try:
        logger.info(f"Generating description for image: {image_url}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://platform-openai-wrapper-service-dev-547175224231.us-central1.run.app/openai/image-to-description",
                json={
                    "image_url": str(image_url),
                    "user_prompt": user_prompt,
                    "focus_entity": focus_entitiy,
                    "trigger_word": trigger_word,
                },
            ) as response:
                response_data = await response.json()
                description = response_data.get("data", {}).get(
                    "description", "No description found"
                )

                logger.info(f"Received description: {description}")
                return description
    except Exception as e:
        logger.error(f"Failed to generate description for {image_url}: {e}")
        return f"Failed to generate description: {str(e)}"
