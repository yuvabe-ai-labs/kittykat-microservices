import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
from helpers.watermarking_utils import (
    encode_image_to_base64,
    get_position,
)
from constants.path_constants import FONTS_DIR


router = APIRouter()


@router.post("/watermark/text")
async def apply_text_watermark(
    original_images: List[UploadFile] = File(...),
    watermark_text: str = Form("KITTYKAT"),
    font_name: str = Form("8bitlim.ttf"),
    font_scale: Optional[float] = Form(0.05),
    opacity: Optional[float] = Form(50.0),
    font_color: List[int] = Form(
        [255, 255, 255]
    ),  # Expecting font color as a list of integers
    position: Optional[str] = Form("bottom_right"),
):
    watermarked_images = []

    font_path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found.")

    if len(font_color) != 3 or any(c < 0 or c > 255 for c in font_color):
        raise HTTPException(
            status_code=400,
            detail="Invalid font color format. Provide three values in range 0-255.",
        )

    text_opacity = int((opacity / 100) * 255)
    text_color = tuple(font_color) + (text_opacity,)

    for original_image in original_images:
        with Image.open(original_image.file).convert("RGBA") as img:
            font_size = int(img.width * font_scale)
            font = ImageFont.truetype(font_path, font_size)

            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width, text_height = (
                text_bbox[2] - text_bbox[0],
                text_bbox[3] - text_bbox[1],
            )
            pos = get_position(position, img, text_width, text_height)

            draw.text(pos, watermark_text, fill=text_color, font=font)
            watermarked_image = Image.alpha_composite(img, overlay)
            watermarked_images.append(encode_image_to_base64(watermarked_image))

    return JSONResponse(content={"images": watermarked_images})
