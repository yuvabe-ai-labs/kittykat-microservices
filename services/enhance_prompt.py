import aiohttp


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
