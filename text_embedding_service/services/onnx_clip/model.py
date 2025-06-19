import errno
import os
import logging
from pathlib import Path
from typing import List, Tuple, Union, Iterable, Iterator, TypeVar, Optional
import requests

import numpy as np
import onnxruntime as ort
from PIL import Image


from .tokenizer import Tokenizer


class OnnxClip:
    """
    This class can be utilised to predict the most relevant text snippet, given
    an image, without directly optimizing for the task, similarly to the
    zero-shot capabilities of GPT-2 and 3. The difference between this class
    and [CLIP](https://github.com/openai/CLIP) is that here we don't depend on
    `torch` or `torchvision`.
    """

    def __init__(
        self,
        model: str = "ViT-B/32",
        batch_size: Optional[int] = None,
        silent_download: bool = False,
        cache_dir: Optional[str] = None,
    ):
        """
        Instantiates the model and required encoding classes.

        Args:
            model: The model to utilise. Currently ViT-B/32 and RN50 are
                allowed.
            batch_size: If set, splits the lists in `get_image_embeddings`
                and `get_text_embeddings` into batches of this size before
                passing them to the model. The embeddings are then concatenated
                back together before being returned. This is necessary when
                passing large amounts of data (perhaps ~100 or more).
            silent_download: If True, the function won't show a warning in
                case when the models need to be downloaded from the S3 bucket.
            cache_dir: If provided, the models will be downloaded to / loaded from this location
        """
        allowed_models = ["ViT-B/32", "RN50"]
        if model not in allowed_models:
            raise ValueError(f"`model` must be in {allowed_models}. Got {model}.")
        if model == "ViT-B/32":
            self.embedding_size = 512
        elif model == "RN50":
            self.embedding_size = 1024
        self.text_model = self._load_models(model, silent_download, cache_dir=cache_dir)
        self._tokenizer = Tokenizer()
        self._batch_size = batch_size

    @property
    def EMBEDDING_SIZE(self):
        raise RuntimeError(
            "OnnxModel.EMBEDDING_SIZE is no longer supported, please use the instance attribute: onnx_model.embedding_size"
        )

    @staticmethod
    def _load_models(
        model: str, silent: bool, cache_dir: Optional[str]
    ) -> ort.InferenceSession:
        """
        Grabs the ONNX implementation of CLIP's model :
        https://github.com/openai/CLIP/blob/main/clip/model.py

        We have exported it to ONNX to remove the dependency on `torch` and
        `torchvision`.

        cache_dir: If provided, the models will be downloaded to / loaded from this location
        """
        if model == "ViT-B/32":
            # IMAGE_MODEL_FILE = "clip_image_model_vitb32.onnx"
            TEXT_MODEL_FILE = "clip_text_model_vitb32.onnx"
        elif model == "RN50":
            # IMAGE_MODEL_FILE = "clip_image_model_rn50.onnx"
            TEXT_MODEL_FILE = "clip_text_model_rn50.onnx"
        else:
            raise ValueError(f"Unexpected model {model}. No `.onnx` file found.")
        if cache_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(base_dir, "data")

        path = os.path.join(cache_dir, TEXT_MODEL_FILE)
        loaded_model = OnnxClip._load_model(path, silent)

        return loaded_model

    @staticmethod
    def _load_model(path: str, silent: bool):
        try:
            if os.path.exists(path):
                # `providers` need to be set explicitly since ORT 1.9
                return ort.InferenceSession(
                    path, providers=ort.get_available_providers()
                )
            else:
                raise FileNotFoundError(
                    errno.ENOENT,
                    os.strerror(errno.ENOENT),
                    path,
                )
        except Exception:
            s3_url = f"https://lakera-clip.s3.eu-west-1.amazonaws.com/{os.path.basename(path)}"
            if not silent:
                logging.info(
                    f"The model file ({path}) doesn't exist "
                    f"or it is invalid. Downloading it from the public S3 "
                    f"bucket: {s3_url}."  # noqa: E501
                )

            # Download from S3
            # Saving to a temporary file first to avoid corrupting the file
            temporary_filename = Path(path).with_name(os.path.basename(path) + ".part")

            # Create any missing directories in the path
            temporary_filename.parent.mkdir(parents=True, exist_ok=True)

            with requests.get(s3_url, stream=True) as r:
                r.raise_for_status()
                with open(temporary_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                    f.flush()
            # Finally move the temporary file to the correct location
            temporary_filename.rename(path)

            # `providers` need to be set explicitly since ORT 1.9
            return ort.InferenceSession(path, providers=ort.get_available_providers())

    def get_text_embeddings(
        self, texts: Iterable[str], with_batching: bool = True
    ) -> np.ndarray:
        """Compute the embeddings for a list of texts.

        Args:
            texts: A list of texts to run on. Each entry can be at most
                77 characters.
            with_batching: Whether to use batching - see the `batch_size` param
                in `__init__()`

        Returns:
            An array of embeddings of shape (len(texts), embedding_size).
        """
        if not with_batching or self._batch_size is None:
            text = self._tokenizer.encode_text(texts)
            if len(text) == 0:
                return self._get_empty_embedding()

            return self.text_model.run(None, {"TEXT": text})[0]
        else:
            embeddings = []
            for batch in to_batches(texts, self._batch_size):
                embeddings.append(self.get_text_embeddings(batch, with_batching=False))

            if not embeddings:
                return self._get_empty_embedding()

            return np.concatenate(embeddings)

    def _get_empty_embedding(self):
        return np.empty((0, self.embedding_size), dtype=np.float32)


T = TypeVar("T")


def to_batches(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Splits an iterable (e.g. a list) into batches of length `size`. Includes
    the last, potentially shorter batch.

    Examples:
        >>> list(to_batches([1, 2, 3, 4], size=2))
        [[1, 2], [3, 4]]
        >>> list(to_batches([1, 2, 3, 4, 5], size=2))
        [[1, 2], [3, 4], [5]]

        # To limit the number of batches returned
        # (avoids reading the rest of `items`):
        >>> import itertools
        >>> list(itertools.islice(to_batches([1, 2, 3, 4, 5], size=2), 1))
        [[1, 2]]

    Args:
        items: The iterable to split.
        size: How many elements per batch.
    """
    if size < 1:
        raise ValueError("Chunk size must be positive.")

    batch = []
    for item in items:
        batch.append(item)

        if len(batch) == size:
            yield batch
            batch = []

    # The last, potentially incomplete batch
    if batch:
        yield batch
