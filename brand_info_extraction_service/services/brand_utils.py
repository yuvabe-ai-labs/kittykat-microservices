from openai import OpenAI
import asyncio
from services.color_scrap_utils import extract_dominant_colors
from services.fonts_utils import extract_fonts
from services.title_and_desc_utils import extract_title_desc
from services.logo_scrap_utils import extract_logos
from services.favicon_utils import extract_favicon_url
from dotenv import load_dotenv
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def generate_brand_json(url):
    """
    Generates a JSON output with brand details based on the extracted information.

    Parameters:
        url(str) : url of the brand
    
    Returns:
        dict: A JSON object with brand details.
    """
    logger.info(f"Starting to generate brand JSON for URL: {url}")

    # Extract brand details
    try:
        logger.info("Extracting brand title and description...")
        brand_name, brand_description = await extract_title_desc(url)
        logger.info(f"Brand name and description extracted: {brand_name}, {brand_description}")
    except Exception as e:
        logger.error(f"Error extracting title and description: {e}")
        brand_name, brand_description = "Unknown", "No description available"

    try:
        logger.info("Extracting brand dominant colors...")
        brand_colors = await extract_dominant_colors(url)
        logger.info(f"Extracted dominant colors: {brand_colors}")
    except Exception as e:
        logger.error(f"Error extracting colors: {e}")
        brand_colors = []

    try:
        logger.info("Extracting brand logos...")
        brand_logo = await extract_logos(url)
        logger.info(f"Extracted logos: {brand_logo}")
    except Exception as e:
        logger.error(f"Error extracting logos: {e}")
        brand_logo = []

    try:
        logger.info("Extracting brand fonts...")
        brand_fonts = await extract_fonts(url)
        logger.info(f"Extracted fonts: {brand_fonts}")
    except Exception as e:
        logger.error(f"Error extracting fonts: {e}")
        brand_fonts = []

    try:
        logger.info("Extracting favicon...")
        favicons = await extract_favicon_url(url)
        logger.info(f"Extracted favicon: {favicons}")
    except Exception as e:
        logger.error(f"Error extracting favicon: {e}")
        favicons = []

    logger.info("Web scraping completed successfully, preparing OpenAI prompt...")

    prompt = f"""
        Based on the following brand details, generate a JSON object with the given structure:
        {{
        "brand_name": "{brand_name}",  # Ignore unnecessary data except title or brand name
        "brand_category": ["",""],  # Inferred categories based on the brand details -> {brand_description},..Inference the categorize based on the description for example Technology,clothing,pc building and put into a list 
        "brand_description": "{brand_description}",  # Inferred proper description -> {brand_description}, summarize it for a more understandable description
        "brand_colors": [{', '.join([f'"{color}"' for color in brand_colors])}],  # Ensure colors are in a list format
        "brand_fonts": [{', '.join([f'"{font}"' for font in brand_fonts])}],  # Ensure fonts are in a list format and only include valid fonts
        "brand_logo": [{', '.join([f'"{logo}"' for logo in brand_logo])}]  # Validate and include only perfect URLs for the company logo(s) rather than the path, avoiding non-standard or duplicate logos
        "favicon" : [{favicons}]  # put the favicon into the list
        }}
        """

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found in environment variables!")
        return {"error": "OpenAI API key not found"}

    try:
        logger.info("Making API request to OpenAI...")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}, {"role": "system", "content": "HTML Content Extractor"}],
            temperature=0.7
        )

        output = response.choices[0].message.content
        logger.info("OpenAI response received successfully")
        return output
    except Exception as e:
        logger.error(f"Error making OpenAI API request: {e}")
        return {"error": f"Error making OpenAI API request: {e}"}

# Example usage
# sample_url = "https://eu.venchi.com/"
# sample_out = await generate_brand_json(sample_url)
# print(sample_out)
