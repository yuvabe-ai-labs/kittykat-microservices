from openai import OpenAI
import asyncio
from services.web_scrap_utils import extract_brand_details
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
        logger.info("Extracting brand details...")
        brand_name, brand_description,brand_colors,brand_logo,brand_fonts,brand_favicons = await extract_brand_details(url)
        logger.info(f"Brand details extracted sucessfully")
    except Exception as e:
        logger.error(f"Error extracting brand details: {e}")
        brand_name, brand_description = "Unknown", "No description available"
        brand_colors=[]
        brand_favicons=""
        brand_colors=[]
        brand_fonts=[]
        brand_logo=[]


    logger.info("Web scraping completed successfully, preparing OpenAI prompt...")

    prompt = f"""
        Based on the following brand details, generate a JSON object with the given structure: 
        {{
        "brand_name": "{brand_name}",  # Extract the brand name from the title and remove any unrelated or descriptive parts. The brand name is usually the most distinct and recognizable term. Please provide just the brand name as the output.
        "brand_category": ["",""],  # Inferred categories based on the brand details -> {brand_description},..Inference the categorize based on the description for example Technology,clothing,pc building and put into a list 
        "brand_description": "{brand_description}",  # Inferred proper description -> {brand_description}, summarize it for a more understandable description
        "brand_colors": [{', '.join([f'"{color}"' for color in brand_colors])}],  # Ensure colors are in a list format
        "brand_fonts": [{', '.join([f'"{font}"' for font in brand_fonts])}],  # Ensure fonts are in a list format and only include valid fonts,ignore the count of the fonts
        "brand_logo": [{', '.join([f'"{logo}"' for logo in brand_logo if 'logo' in logo.lower() or 'brand' in logo.lower() or 'icon' in logo.lower()])} ],  # Validate and include only distinct URLs for company logos. Ignore non-logo or placeholder images.
        "favicon" : [{brand_favicons}]  # put the favicon into the list
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
# sample_out = asyncio.run(generate_brand_json(sample_url))
# print(sample_out)
