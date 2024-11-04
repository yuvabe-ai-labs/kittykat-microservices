from io import BytesIO
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import requests
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
from helpers.watermarking_utils import (
    encode_image_to_base64,
    get_position,
    upload_to_gcs,
)
from constants.path_constants import FONTS_DIR

router = APIRouter()


@router.post("/file/watermark/text")
async def apply_text_watermark(
    original_images: List[UploadFile] = File(...),
    watermark_text: str = Form("KITTYKAT"),
    font_name: str = Form("8bitlim.ttf"),
    font_scale: Optional[float] = Form(0.05),
    opacity: Optional[float] = Form(50.0),
    font_color: str = Form("255,255,255"),
    position: Optional[str] = Form("bottom_right"),
):
    watermarked_images = []

    # Validate font path
    font_path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found.")

    # Parse and validate font color
    try:
        font_color_rgb = tuple(int(c) for c in font_color.split(","))
        if len(font_color_rgb) != 3 or any(c < 0 or c > 255 for c in font_color_rgb):
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid font color format. Provide three comma-separated values in range 0-255.",
        )

    # Calculate text color with opacity
    text_opacity = int((opacity / 100) * 255)
    text_color = font_color_rgb + (text_opacity,)

    # Process each uploaded image
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


@router.post("/url/watermark/text")
async def apply_text_watermark_from_urls(
    image_urls: List[str] = Form(...),
    watermark_text: str = Form("KITTYKAT"),
    font_name: str = Form("8bitlim.ttf"),
    font_scale: Optional[float] = Form(0.05),
    opacity: Optional[float] = Form(50.0),
    font_color: str = Form("255,255,255"),
    position: Optional[str] = Form("bottom_right"),
):
    watermarked_images = []

    # Validate font path
    font_path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found.")

    # Parse and validate font color
    try:
        font_color_rgb = tuple(int(c) for c in font_color.split(","))
        if len(font_color_rgb) != 3 or any(c < 0 or c > 255 for c in font_color_rgb):
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid font color format. Provide three comma-separated values in range 0-255.",
        )

    # Calculate text color with opacity
    text_opacity = int((opacity / 100) * 255)
    text_color = font_color_rgb + (text_opacity,)

    # Process each image URL
    for image_url in image_urls:
        try:
            # Download image from URL
            response = requests.get(image_url)
            response.raise_for_status()
            original_image = Image.open(BytesIO(response.content)).convert("RGBA")
        except requests.exceptions.RequestException:
            raise HTTPException(
                status_code=400, detail=f"Unable to fetch image from URL: {image_url}"
            )

        # Apply watermark
        font_size = int(original_image.width * font_scale)
        font = ImageFont.truetype(font_path, font_size)

        overlay = Image.new("RGBA", original_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = (
            text_bbox[2] - text_bbox[0],
            text_bbox[3] - text_bbox[1],
        )
        pos = get_position(position, original_image, text_width, text_height)

        draw.text(pos, watermark_text, fill=text_color, font=font)
        watermarked_image = Image.alpha_composite(original_image, overlay)

        # Encode the watermarked image to base64
        encoded_image = encode_image_to_base64(watermarked_image)
        watermarked_images.append(encoded_image)

    return JSONResponse(content={"images": watermarked_images})


@router.post("/file/watermark/image/store/files")
async def apply_text_watermark_from_files(
    original_images: List[UploadFile] = File(...),
    file_names: List[str] = Form(...),  # Accepts a list of desired file names
    watermark_text: str = Form("KITTYKAT"),
    font_name: str = Form("8bitlim.ttf"),
    font_scale: Optional[float] = Form(0.05),
    opacity: Optional[float] = Form(50.0),
    font_color: str = Form("255,255,255"),
    position: Optional[str] = Form("bottom_right"),
    folder_path: str = Form(...),
):
    if len(original_images) != len(file_names):
        raise HTTPException(
            status_code=400,
            detail="The number of images must match the number of file names.",
        )

    watermarked_images = []

    # Validate font path
    font_path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found.")

    # Parse and validate font color
    try:
        font_color_rgb = tuple(int(c) for c in font_color.split(","))
        if len(font_color_rgb) != 3 or any(c < 0 or c > 255 for c in font_color_rgb):
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid font color format. Provide three comma-separated values in range 0-255.",
        )

    # Calculate text color with opacity
    text_opacity = int((opacity / 100) * 255)
    text_color = font_color_rgb + (text_opacity,)

    # Process each uploaded image
    for original_image, file_name in zip(original_images, file_names):
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

            # Upload to GCS and get the URL
            image_url = upload_to_gcs(watermarked_image, folder_path, file_name)
            watermarked_images.append(image_url)

    return JSONResponse(content={"images": watermarked_images})


@router.post("/file/watermark/url/store/files")
async def apply_text_watermark_from_urls(
    image_urls: List[str] = Form(...),
    file_names: List[str] = Form(...),  # Accepts a list of desired file names
    watermark_text: str = Form("KITTYKAT"),
    font_name: str = Form("8bitlim.ttf"),
    font_scale: Optional[float] = Form(0.05),
    opacity: Optional[float] = Form(50.0),
    font_color: str = Form("255,255,255"),
    position: Optional[str] = Form("bottom_right"),
    folder_path: str = Form(...),
):
    if len(image_urls) != len(file_names):
        raise HTTPException(
            status_code=400,
            detail="The number of image URLs must match the number of file names.",
        )

    watermarked_images = []

    # Validate font path
    font_path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found.")

    # Parse and validate font color
    try:
        font_color_rgb = tuple(int(c) for c in font_color.split(","))
        if len(font_color_rgb) != 3 or any(c < 0 or c > 255 for c in font_color_rgb):
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid font color format. Provide three comma-separated values in range 0-255.",
        )

    # Calculate text color with opacity
    text_opacity = int((opacity / 100) * 255)
    text_color = font_color_rgb + (text_opacity,)

    # Process each image URL
    for image_url, file_name in zip(image_urls, file_names):
        response = requests.get(image_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail=f"Image not found at {image_url}"
            )

        with Image.open(BytesIO(response.content)).convert("RGBA") as img:
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

            # Upload to GCS and get the URL
            image_url = upload_to_gcs(watermarked_image, folder_path, file_name)
            watermarked_images.append(image_url)

    return JSONResponse(content={"images": watermarked_images})
