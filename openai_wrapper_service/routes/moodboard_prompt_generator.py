import json
from fastapi import APIRouter
from models.moodboard_prompt_generator import (
    MoodboardPromptsResponse,
    MoodboardPromptsRequest,
)
from models.global_models import GeneralResponse
from constants.assistants import MOODBOARD_PROMPT_GENERATOR_ASSISTANT_ID
from services.openai import submit_message, get_response
from config.logger import logger

router = APIRouter()


@router.post("/moodboard/prompts", response_model=GeneralResponse)
async def generate_moodboard_prompts(request: MoodboardPromptsRequest):
    """
    Generates moodboard prompts based on brand and project details using OpenAI Assistant Beta.
    Accepts JSON input for brand_details and project_details.
    """
    # Validate input data
    if not request.brand_details or not request.project_details:
        logger.warning("Missing required details: brand_details or project_details.")
        return GeneralResponse(
            status_code=400,
            data=None,
            message="Both brand_details and project_details must be provided.",
        )

    try:
        # Log the incoming request data
        logger.info(f"Received request to generate moodboard prompts: {request.dict()}")

        # Prepare the JSON data to be sent to OpenAI Assistant Beta
        request_data = {
            "no_of_prompts_required": request.no_of_prompts,
            "brand_details": request.brand_details,
            "project_details": request.project_details,
        }

        request_data_json = json.dumps(request_data)

        # Submit the request message to OpenAI
        logger.info("Submitting message to OpenAI Assistant Beta for thread creation.")
        thread_id, run_id = await submit_message(
            request_data_json, MOODBOARD_PROMPT_GENERATOR_ASSISTANT_ID
        )

        # Retrieve the response from OpenAI Assistant Beta
        logger.info(
            f"Waiting for OpenAI response. Thread ID: {thread_id}, Run ID: {run_id}"
        )
        data = await get_response(thread_id, run_id)

        # Check if the response contains valid data
        if not data:
            logger.error("Failed to retrieve valid prompts from OpenAI.")
            return GeneralResponse(
                status_code=500,
                data=None,
                message="Failed to retrieve valid prompts from OpenAI Assistant Beta.",
            )

        logger.info(f"Successfully generated {len(data)} moodboard prompts.")

        return GeneralResponse(
            status_code=200,
            data=MoodboardPromptsResponse(image_prompts=data),
            message="Successfully Generated Prompts",
        )

    except json.JSONDecodeError as json_error:
        logger.error(f"Error decoding JSON: {json_error}")
        return GeneralResponse(
            status_code=500,
            data=None,
            message="An error occurred while processing JSON data.",
        )

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return GeneralResponse(#/
            status_code=500,
            data=None,
            message=f"An unexpected error occurred: {str(e)}",
        )
