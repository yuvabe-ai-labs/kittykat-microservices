import json
from fastapi import APIRouter
from services.openai import get_response_from_assistant, submit_message
from config.logger import logger
from constants.assistants import JSON_CONVERTER_ASSISTANT_ID
from models.json_converter_models import JsonConverterRequest, JsonConverterResponse
from models.global_models import GeneralResponse

router = APIRouter()


@router.post("/json/convert", response_model=GeneralResponse)
async def convert_to_json(request: JsonConverterRequest):
    """
    Convert input data into JSON format using OpenAI Assistant.
    """
    if not request.data.strip() or not request.fields:
        logger.warning("Empty data or fields provided.")
        return GeneralResponse(
            status_code=400, data=None, message="Data and fields cannot be empty."
        )

    try:
        logger.info(f"Received data for JSON conversion: {request.data}")
        logger.info(f"Fields for conversion: {request.fields}")

        request_data = {
            "data": request.data,
            "fields": request.fields,
            "type": request.type,
        }
        request_data_json = json.dumps(request_data)

        logger.info("Submitting request to OpenAI Assistant for JSON conversion.")
        thread_id, run_id = await submit_message(
            request_data_json, JSON_CONVERTER_ASSISTANT_ID
        )
        logger.info(
            f"Waiting for response from OpenAI. Thread ID: {thread_id}, Run ID: {run_id}"
        )
        converted_json = await get_response_from_assistant(
            thread_id, run_id, response_key="data"
        )

        if converted_json:
            return GeneralResponse(
                status_code=200,
                data=JsonConverterResponse(converted_json=converted_json),
                message="Data converted to JSON successfully.",
            )
        else:
            return GeneralResponse(
                status_code=500, data=None, message="Failed to retrieve converted JSON."
            )

    except Exception as e:
        logger.error(f"An error occurred while converting data to JSON: {str(e)}")
        return GeneralResponse(
            status_code=500,
            data=None,
            message=f"An unexpected error occurred: {str(e)}",
        )
