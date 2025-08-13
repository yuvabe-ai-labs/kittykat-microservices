from typing import Optional
from pydantic import BaseModel
from enum import Enum


class ScaleFactor(str, Enum):
    TWO_X = "2x"
    FOUR_X = "4x"
    EIGHT_X = "8x"
    SIXTEEN_X = "16x"


class OptimizedFor(str, Enum):
    STANDARD = "standard"
    SOFT_PORTRAITS = "soft_portraits"
    HARD_PORTRAITS = "hard_portraits"
    ART_N_ILLUSTRATION = "art_n_illustration"
    VIDEOGAME_ASSETS = "videogame_assets"
    NATURE_N_LANDSCAPES = "nature_n_landscapes"
    FILMS_N_PHOTOGRAPHY = "films_n_photography"
    THREE_D_RENDERS = "3d_renders"
    SCIENCE_FICTION_N_HORROR = "science_fiction_n_horror"


class Engine(str, Enum):
    AUTOMATIC = "automatic"
    MAGNIFIC_ILLUSIO = "magnific_illusio"
    MAGNIFIC_SHARPY = "magnific_sharpy"
    MAGNIFIC_SPARKLE = "magnific_sparkle"


class ImageUpscaleRequest(BaseModel):
    image_url: str  # Base64 encoded image string
    webhook_url: Optional[str] = None  # Optional callback URL
    scale_factor: Optional[ScaleFactor] = ScaleFactor.TWO_X  # 2x, 4x, 8x, 16x
    # standard, soft_portraits, etc.
    optimized_for: Optional[OptimizedFor] = OptimizedFor.STANDARD
    prompt: Optional[str] = None
    creativity: Optional[int] = 0  # Range -10 to 10
    hdr: Optional[int] = 0  # Range -10 to 10
    resemblance: Optional[int] = 0  # Range -10 to 10
    fractality: Optional[int] = 0  # Range -10 to 10
    # automatic, magnific_illusio, etc.
    engine: Optional[Engine] = Engine.AUTOMATIC
