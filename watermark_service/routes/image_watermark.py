from io import BytesIO
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import requests
from helpers.watermarking_utils import (
    load_watermark_image,
    encode_image_to_base64,
    get_position,
    apply_opacity,
    resize_image,
    upload_to_gcs,
)

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SAFE_PIXEL_LIMIT = 178956970


@router.post("/file/watermark/image")
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


@router.post("/url/watermark/image")
async def apply_watermark_from_urls(
    image_urls: List[str] = Form(...),
    watermark_image: Optional[UploadFile] = File(None),
    watermark_scale: Optional[float] = Form(0.15),
    position: Optional[str] = Form("bottom_right"),
    opacity: Optional[float] = Form(100.0),
):
    try:
        # Load and process watermark image
        watermark = load_watermark_image(watermark_image)
        watermarked_images = []

        for image_url in image_urls:
            # Download the image from the URL
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                original = Image.open(BytesIO(response.content)).convert("RGBA")
            except requests.exceptions.RequestException:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to fetch image from URL: {image_url}",
                )

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


@router.post("/file/watermark/image/store")
async def apply_watermark_and_store(
    original_images: List[UploadFile] = File(...),
    file_names: List[str] = Form(...),
    watermark_image: Optional[UploadFile] = File(None),
    watermark_scale: Optional[float] = Form(0.15),
    position: Optional[str] = Form("bottom_right"),
    opacity: Optional[float] = Form(100.0),
    folder_paths: List[str] = Form(...),  # Accepting a list of folder paths
    bucket_name: Optional[str] = Form(
        None
    ),  # Accepting the bucket name from the request
):
    try:
        logger.info("Received request to apply watermark and store images.")

        # Check if bucket_name is provided
        if not bucket_name:
            logger.error("Bucket name is required but not provided.")
            return JSONResponse(
                status_code=400,
                content={"error": "Bucket name is required."},
            )

        # Load watermark image
        watermark = load_watermark_image(watermark_image)
        watermarked_images = []

        # Validate that the lengths of input lists match
        if len(original_images) != len(file_names) or len(original_images) != len(
            folder_paths
        ):
            logger.error("Number of images, file names, and folder paths do not match.")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Number of images, file names, and folder paths must match."
                },
            )

        logger.info(f"Processing {len(original_images)} images for watermarking.")

        for original_image, file_name, folder_path in zip(
            original_images, file_names, folder_paths
        ):
            logger.info(f"Processing image: {file_name} in folder: {folder_path}")

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

                # Upload to GCS and get the URL, using the provided bucket_name
                image_url = upload_to_gcs(
                    watermarked_image, folder_path, file_name, bucket_name
                )
                watermarked_images.append(image_url)

        logger.info(f"Successfully processed {len(watermarked_images)} images.")
        return JSONResponse(content={"images": watermarked_images})

    except Exception as e:
        logger.exception("An error occurred while processing the watermark.")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/url/watermark/image/store")
async def apply_watermark_from_urls(
    image_urls: List[str] = Form(...),
    file_names: List[str] = Form(...),
    watermark_image: Optional[UploadFile] = File(None),
    watermark_scale: Optional[float] = Form(0.15),
    position: Optional[str] = Form("bottom_right"),
    opacity: Optional[float] = Form(100.0),
    folder_paths: List[str] = Form(...),
    bucket_name: Optional[str] = Form(None),
):
    """
    Apply watermark to images from a list of URLs, upload to GCS, and return the URLs.
    """
    try:
        print("test")
        logger.info("Received request to apply watermark and store images from URLs.")

        if not bucket_name:
            logger.error("Bucket name is required but not provided.")
            return JSONResponse(
                status_code=400,
                content={"error": "Bucket name is required."},
            )

        logger.info(f"Loading watermark image.")
        watermark = load_watermark_image(watermark_image)

        if len(image_urls) != len(file_names) or len(file_names) != len(folder_paths):
            logger.error(
                "Mismatch in the number of URLs, file names, and folder paths."
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Number of image URLs, file names, and folder paths must match."
                },
            )

        logger.info(f"Processing {len(image_urls)} images from URLs.")
        watermarked_images = []

        for idx, image_url in enumerate(image_urls):
            logger.info(f"Processing image {idx + 1}: {image_url}")

            try:
                # Download image
                logger.debug(f"Downloading image from URL: {image_url}")
                response = requests.get(image_url)
                response.raise_for_status()
                logger.debug(
                    f"Downloaded image: {image_url}, Size: {len(response.content)} bytes"
                )

                # Disable decompression bomb check temporarily
                Image.MAX_IMAGE_PIXELS = None

                with Image.open(BytesIO(response.content)) as original:
                    original_size = original.size
                    logger.debug(f"Opened image: {original_size[0]}x{original_size[1]}")

                    # Resize the image
                    original = resize_image(original)
                    original = original.convert("RGBA")

                    # Resize watermark based on the original image size
                    target_width = int(original.width * watermark_scale)
                    aspect_ratio = target_width / watermark.width
                    target_height = int(watermark.height * aspect_ratio)
                    resized_watermark = watermark.resize(
                        (target_width, target_height), Image.LANCZOS
                    )

                    # Log watermark size
                    logger.debug(
                        f"Watermark resized to: {resized_watermark.size[0]}x{resized_watermark.size[1]}"
                    )

                    # Apply opacity and position to watermark
                    resized_watermark = apply_opacity(resized_watermark, opacity)
                    pos = get_position(
                        position,
                        original,
                        resized_watermark.width,
                        resized_watermark.height,
                    )
                    logger.debug(f"Applying watermark at position: {position}")

                    # Create the watermarked image
                    watermarked_image = original.copy()
                    watermarked_image.paste(resized_watermark, pos, resized_watermark)

                    # Upload to GCS
                    file_name = file_names[idx]
                    folder_path = folder_paths[idx]
                    logger.debug(
                        f"Uploading watermarked image to GCS, file name: {file_name}, folder path: {folder_path}"
                    )
                    image_url = upload_to_gcs(
                        watermarked_image, folder_path, file_name, bucket_name
                    )
                    logger.debug(f"Uploaded image to GCS: {image_url}")

                    # Add the uploaded image URL to the list
                    watermarked_images.append(image_url)

            except requests.RequestException as e:
                logger.error(f"Error downloading image {image_url}: {str(e)}")
                continue  # Skip the current image and move to the next one

            except Exception as e:
                logger.exception(f"Error processing image {image_url}: {str(e)}")
                continue  # Skip the current image and move to the next one

            finally:
                # Restore the decompression bomb limit
                Image.MAX_IMAGE_PIXELS = SAFE_PIXEL_LIMIT

        logger.info(f"Successfully processed {len(watermarked_images)} images.")
        return JSONResponse(content={"images": watermarked_images})

    except Exception as e:
        logger.exception("An unexpected error occurred while processing the watermark.")
        return JSONResponse(status_code=500, content={"error": str(e)})
