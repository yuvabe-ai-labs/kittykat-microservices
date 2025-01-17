import asyncio
import json
from config.openai import client
from config.logger import logger


async def submit_message(data, assistant_id):
    """
    Function to submit a message to OpenAI Assistant Beta.

    Args:
        data (str): The message to be sent to the assistant.
        assistant_id (str): The ID of the assistant.

    Returns:
        tuple: (thread_id, run_id) if successful, None if an error occurs.
    """
    try:
        # Create a new thread for communication
        thread = client.beta.threads.create()
        thread_id = thread.id
        logger.info(f"Created new thread with ID: {thread_id}")

        # Send the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=data
        )
        logger.info(f"Message sent to assistant: {data}")

        # Run the assistant on the thread
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        run_id = run.id
        logger.info(f"Assistant run started with ID: {run_id}")

        return thread_id, run_id

    except Exception as e:
        logger.error(f"Error in submitting message: {e}")
        return None


async def get_response_from_assistant(
    thread_id, run_id, max_retries=10, retry_delay=2, response_key=None
):
    """
    General function to retrieve a response from the assistant after a delay if necessary.

    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the assistant run.
        max_retries (int): Maximum number of retries before giving up.
        retry_delay (int): Delay between retries in seconds.
        response_key (str): The key to retrieve specific data (e.g., "image_prompts" or "enhanced_prompt").

    Returns:
        str or list: The response data if successful, None if an error occurs.
    """
    retries = 0
    try:
        # Retry logic for thread status
        while retries < max_retries:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status == "completed":
                logger.info(f"Run {run_id} completed successfully!")
                break
            elif run.status == "failed":
                logger.error(f"Run {run_id} failed: {run.error}")
                return None
            elif run.status == "cancelled":
                logger.warning(f"Run {run_id} was cancelled.")
                return None
            else:
                retries += 1
                logger.info(
                    f"Run {run_id} status: {run.status}. Retrying ({retries}/{max_retries})..."
                )
                await asyncio.sleep(retry_delay)

        else:
            logger.error(f"Max retries reached for run {run_id}. Exiting.")
            return None

        # Retrieving the messages from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            if message.role == "assistant":
                logger.info(
                    f"Assistant response for thread {thread_id}: {message.content[0].text.value}"
                )

                try:
                    value = message.content[0].text.value
                    response_data = json.loads(value)

                    # Dynamically retrieve the required key (e.g., image_prompts or enhanced_prompt)
                    if response_key:
                        return response_data.get(response_key, None)
                    else:
                        return response_data

                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing assistant message content: {e}")
                    return None

    except Exception as e:
        logger.error(
            f"An unexpected error occurred while retrieving the response for run {run_id}: {e}"
        )
        return None
