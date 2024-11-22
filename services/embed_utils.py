import numpy as np
from .onnx_clip.model import OnnxClip
from PIL import Image
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
    return (embedding / norm).tolist()


def image_embed(image_to_embed):
    """
    Extracts and normalizes embeddings for a single image.

    Parameters:
        image_to_embed (PIL.Image.Image): The input image to generate embeddings for.

    Returns:
        list: The normalized embedding for the input image.
    """
    # Generate image embeddings using the ONNX model
    image_embeddings = onnx_model.get_image_embeddings([image_to_embed])
    # Normalize the embeddings
    return normalize_embedding(image_embeddings[0])


async def send_img_to_embed(input_img):
    """
    Processes a single image asynchronously to generate embeddings.

    Parameters:
        input_img (PIL.Image.Image): The input image to embed.

    Returns:
        list: The normalized embedding for the input image.
    """
    # Get the current event loop
    loop = asyncio.get_event_loop()
    # Run the image embedding process in a separate thread
    return await loop.run_in_executor(None, image_embed, input_img)


async def batch_image_embed(images_to_embed):
    """
    Processes multiple images asynchronously to generate embeddings in parallel.

    Parameters:
        images_to_embed (list of PIL.Image.Image): A list of images to embed.

    Returns:
        list of list: A list containing normalized embeddings for each input image.
    """
    # Get the current event loop
    loop = asyncio.get_event_loop()
    # Create asynchronous tasks for embedding each image
    tasks = [loop.run_in_executor(None, image_embed, img) for img in images_to_embed]
    # Wait for all tasks to complete and return the results
    return await asyncio.gather(*tasks)
