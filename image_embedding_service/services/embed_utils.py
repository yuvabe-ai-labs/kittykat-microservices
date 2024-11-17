import numpy as np
from .onnx_clip.model import OnnxClip
from PIL import Image
import asyncio

# Initialize the ONNX model
onnx_model = OnnxClip(batch_size=16)


def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding, ord=2, axis=-1, keepdims=True)
    return (embedding / norm).tolist()  # Convert ndarray to list


def image_embed(image_to_embed):
    image_embeddings = onnx_model.get_image_embeddings([image_to_embed])
    return normalize_embedding(image_embeddings[0])


async def send_img_to_embed(input_img):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, image_embed, input_img)


# Example of batch processing for images
async def batch_image_embed(images_to_embed):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, image_embed, img) for img in images_to_embed]
    return await asyncio.gather(*tasks)
