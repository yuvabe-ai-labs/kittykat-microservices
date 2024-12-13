from openai import OpenAI
from services.color_scrap_utils import extract_dominant_colors
from services.fonts_utils import extract_fonts
from services.title_and_desc_utils import extract_title_desc
from services.logo_scrap_utils import extract_logos
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def generate_brand_json(url):
    """
    Generates a JSON output with brand details based on the extracted information.

    Parameters:
        url(str) : url of the brand
    
    Returns:
        dict: A JSON object with brand details.
    """

    brand_name, brand_description = extract_title_desc(url)
    brand_colors =  extract_dominant_colors(url)
    brand_logo =  extract_logos(url)
    brand_fonts = extract_fonts(url)
    prompt = f"""
        Based on the following brand details, generate a JSON object with the given structure:
        {{
        "brand_name": "{brand_name}",  # Ignore unnecessary data except title or brand name
        "brand_category": ["",""],  # Inferred categories based on the brand details -> {brand_description},..Inference the categorize based on the description for example  Technology,clothing,pc building and put into a list 
        "brand_description": "{brand_description}",  # Inferred proper description -> {brand_description}, summarize it for a more understandable description
        "brand_colors": [{', '.join([f'"{color}"' for color in brand_colors])}],  # Ensure colors are in a list format
        "brand_fonts": [{', '.join([f'"{font}"' for font in brand_fonts])}],  # Ensure fonts are in a list format and only include valid fonts
        "brand_logo": [{', '.join([f'"{logo}"' for logo in brand_logo])}]  # Validate and include only perfect URLs for the company logo(s) rather than the path, avoiding non-standard or duplicate logos
        "favicon" : [] # give favicon if found
        }}
        """

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}, {"role": "system", "content": "HTML Content Extractor"}],
        temperature=0.7
    )
    
    output = response.choices[0].message.content
    return output

# sample_url = "https://eu.venchi.com/"
# sample_out = generate_brand_json(sample_url)
# print(sample_out)