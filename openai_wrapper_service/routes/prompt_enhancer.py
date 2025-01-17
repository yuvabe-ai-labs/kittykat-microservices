import json
from fastapi import APIRouter
from services.openai import get_response_from_assistant, submit_message
from config.logger import logger
from constants.assistants import PROMPT_ENHANCER_ASSISTANT_ID
from models.prompt_enhancer_models import EnhancedPromptResponse, PromptRequest
from models.global_models import GeneralResponse

router = APIRouter()


@router.post("/prompt/enhance", response_model=GeneralResponse)
async def enhance_prompt(request: PromptRequest):
    """
    Enhance a given prompt using OpenAI Assistant.
    """
    if not request.prompt.strip():
        logger.warning("Empty prompt provided.")
        return GeneralResponse(
            status_code=400, data=None, message="Prompt cannot be empty."
        )

    try:
        logger.info(f"Received prompt for enhancement: {request.prompt}")

        request_data = {"prompt": request.prompt}
        request_data_json = json.dumps(request_data)

        logger.info("Submitting request to OpenAI Assistant for enhancement.")
        thread_id, run_id = await submit_message(
            request_data_json, PROMPT_ENHANCER_ASSISTANT_ID
        )
        logger.info(
            f"Waiting for response from OpenAI. Thread ID: {thread_id}, Run ID: {run_id}"
        )
        enhanced_prompt = await get_response_from_assistant(
            thread_id, run_id, response_key="enhanced_prompt"
        )

        if enhanced_prompt:
            return GeneralResponse(
                status_code=200,
                data=EnhancedPromptResponse(enhanced_prompt=enhanced_prompt),
                message="Prompt enhanced successfully.",
            )
        else:
            return GeneralResponse(
                status_code=500,
                data=None,
                message="Failed to retrieve enhanced prompt.",
            )

    except Exception as e:
        logger.error(f"An error occurred while enhancing the prompt: {str(e)}")
        return GeneralResponse(
            status_code=500,
            data=None,
            message=f"An unexpected error occurred: {str(e)}",
        )
