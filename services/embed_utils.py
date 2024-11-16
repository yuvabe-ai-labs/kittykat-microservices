import numpy as np
from .onnx_clip import OnnxClip
import asyncio

# Initialize the ONNX model
onnx_model = OnnxClip(batch_size=16)


def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding, ord=2, axis=-1, keepdims=True)
    return (embedding / norm).tolist()  # Convert ndarray to list


def text_embed(text_to_embed):
    text_embeddings = onnx_model.get_text_embeddings([text_to_embed])
    return normalize_embedding(text_embeddings[0])


async def send_text_to_embed(input_text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, text_embed, input_text)


# Example of batch processing for texts
async def batch_text_embed(texts_to_embed):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, text_embed, txt) for txt in texts_to_embed]
    return await asyncio.gather(*tasks)
