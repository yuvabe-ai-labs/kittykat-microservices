import numpy as np
from .onnx_clip import OnnxClip
import asyncio

# Initialize the ONNX model with a batch size of 16
onnx_model = OnnxClip(batch_size=16)


def normalize_embedding(embedding):
    """
    Normalizes the given embedding vector using L2 normalization.

    Parameters:
        embedding (numpy.ndarray): The input embedding array with shape (N, D),
                                   where N is the batch size and D is the embedding dimension.

    Returns:
        list: The L2-normalized embedding converted to a list.
    """
    norm = np.linalg.norm(embedding, ord=2, axis=-1, keepdims=True)
    return (embedding / norm).tolist()  # Convert ndarray to list for easier handling


def text_embed(text_to_embed):
    """
    Generates and normalizes embeddings for a single text input.

    Parameters:
        text_to_embed (str): The input text to generate embeddings for.

    Returns:
        list: The normalized embedding for the input text.
    """
    # Generate text embeddings using the ONNX model
    text_embeddings = onnx_model.get_text_embeddings([text_to_embed])
    # Normalize the embeddings
    return normalize_embedding(text_embeddings[0])


async def send_text_to_embed(input_text):
    """
    Processes a single text input asynchronously to generate embeddings.

    Parameters:
        input_text (str): The input text to embed.

    Returns:
        list: The normalized embedding for the input text.
    """
    # Get the current event loop
    loop = asyncio.get_event_loop()
    # Run the text embedding process in a separate thread
    return await loop.run_in_executor(None, text_embed, input_text)


async def batch_text_embed(texts_to_embed):
    """
    Processes multiple text inputs asynchronously to generate embeddings in parallel.

    Parameters:
        texts_to_embed (list of str): A list of text strings to embed.

    Returns:
        list of list: A list containing normalized embeddings for each input text.
    """
    # Get the current event loop
    loop = asyncio.get_event_loop()
    # Create asynchronous tasks for embedding each text input
    tasks = [loop.run_in_executor(None, text_embed, txt) for txt in texts_to_embed]
    # Wait for all tasks to complete and return the results
    return await asyncio.gather(*tasks)
