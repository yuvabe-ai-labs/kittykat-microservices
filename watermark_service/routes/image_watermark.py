from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
from helpers.watermarking_utils import (
    load_watermark_image,
    encode_image_to_base64,
    get_position,
    apply_opacity,
)


router = APIRouter()


@router.post("/watermark/image")
async def apply_watermark(
    original_images: List[UploadFile] = File(...),
    watermark_image: Optional[UploadFile] = File(None),
    watermark_scale: Optional[float] = Form(0.15),
    position: Optional[str] = Form("bottom_right"),
    opacity: Optional[float] = Form(100.0),
):
    try:
        watermark = load_watermark_image(watermark_image)
        watermarked_images = []

        for original_image in original_images:
            with Image.open(original_image.file).convert("RGBA") as original:
                # Resize watermark based on original image dimensions
                target_width = int(original.width * watermark_scale)
                aspect_ratio = target_width / watermark.width
                target_height = int(watermark.height * aspect_ratio)
                resized_watermark = watermark.resize(
                    (target_width, target_height), Image.LANCZOS
                )

                # Apply opacity and position watermark
                resized_watermark = apply_opacity(resized_watermark, opacity)
                pos = get_position(
                    position,
                    original,
                    resized_watermark.width,
                    resized_watermark.height,
                )

                # Create watermarked image
                watermarked_image = original.copy()
                watermarked_image.paste(resized_watermark, pos, resized_watermark)
                watermarked_images.append(encode_image_to_base64(watermarked_image))

        return JSONResponse(content={"images": watermarked_images})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
