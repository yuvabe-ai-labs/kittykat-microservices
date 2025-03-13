import os
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
import json
from typing import Dict, List, Union, Optional, Any, AsyncGenerator

from pydantic import HttpUrl
from constants.system_prompts import IMAGE_DESCRIPTION_GENERATER_SYSTEM_PROMPT

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_ai_response(
    system_prompt: str,
    user_messages: List[Union[str, Dict[str, Any]]],
    response_schema: Optional[Dict] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    include_chat_history: bool = False,
    chat_history: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False,
) -> Union[Dict, AsyncGenerator]:
    """
    A flexible function for generating AI responses with optional schema validation, chat history and streaming.

    Args:
        client: The AI client instance (like OpenAI's async client)
        system_prompt: The system prompt to guide the AI
        user_messages: List of user messages (string or dict format)
        response_schema: Optional JSON schema for structured responses
        model: AI model to use
        temperature: Creativity parameter (0.0-1.0)
        max_tokens: Maximum tokens in response (None for default)
        include_chat_history: Whether to include chat history
        chat_history: Optional list of previous conversation messages
        stream: Whether to stream the response

    Returns:
        Parsed JSON response, raw response, or AsyncGenerator for streaming
    """
    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history if requested
    if include_chat_history and chat_history:
        messages.extend(chat_history)

    # Process user messages
    for msg in user_messages:
        if isinstance(msg, str):
            messages.append({"role": "user", "content": msg})
        elif isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append(msg)
        elif isinstance(msg, dict):
            # Handle data dictionary by converting to JSON
            messages.append({"role": "user", "content": json.dumps(msg)})

    # Add schema instruction if provided
    response_format = None
    if response_schema:
        messages.append(
            {
                "role": "user",
                "content": f"Provide a response strictly adhering to this JSON schema: {json.dumps(response_schema)}",
            }
        )
        response_format = {"type": "json_object"}
    # Set up streaming if requested
    if stream:

        async def response_stream():
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            if response_format is not None:
                params["response_format"] = response_format

            stream_response = await async_client.chat.completions.create(**params)

            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        return response_stream()

    # Non-streaming response
    response = await async_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
    )

    result = response.choices[0].message.content

    # Parse JSON if schema was provided
    if response_schema:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback to raw response if JSON parsing fails
            return {"error": "Failed to parse JSON", "raw_response": result}

    return {"response": result}


async def describe_image(
    file_url: HttpUrl,
    user_prompt: str = "Describe this image",
    model: str = "gpt-4o-mini",
) -> str:
    response = await async_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{IMAGE_DESCRIPTION_GENERATER_SYSTEM_PROMPT}",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": file_url}},
                ],
            },
        ],
    )

    return response.choices[0].message.content
