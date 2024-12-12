import json
import requests
from bs4 import BeautifulSoup
from config.openai import client
import re


# Function to fetch HTML content from a URL
async def get_html_content(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise e


# Function to preprocess HTML content and reduce its size
def preprocess_html(soup):
    important_sections = []

    title = soup.title.string if soup.title else "No title found"
    metas = [
        meta.get("content", "") for meta in soup.find_all("meta", attrs={"name": True})
    ]
    headings = [
        heading.get_text(strip=True) for heading in soup.find_all(["h1", "h2", "h3"])
    ]
    links = [link.get("href", "") for link in soup.find_all("a") if link.get("href")]

    favicon = None
    for link in soup.find_all("link", {"rel": "icon"}):
        favicon = link.get("href", "")
        break

    important_sections.append(f"Title: {title}")
    important_sections.append(f"Meta Descriptions: {', '.join(metas)}")
    important_sections.append(f"Headings: {', '.join(headings)}")
    important_sections.append(f"Links: {', '.join(links[:10])}... (and more)")
    important_sections.append(f"Favicon: {favicon if favicon else 'No favicon found'}")

    return soup, "\n".join(important_sections)


# Function to extract colors and fonts from styles
def extract_colors_and_fonts(styles, css_links):
    colors = set()
    fonts = set()

    color_pattern = r"(#(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)"
    font_pattern = r"font-family:\s*([^;]+)"

    for style in styles:
        if style:
            colors.update(re.findall(color_pattern, style))
            fonts.update(re.findall(font_pattern, style))

    for link in css_links:
        pass

    return {"colors": list(colors), "fonts": list(fonts)}


# Function to extract brand data using OpenAI API
async def extract_brand_data(url: str):
    soup = await get_html_content(url)
    soup, preprocessed_content = preprocess_html(soup)

    styles = [style.string for style in soup.find_all("style") if style.string]
    css_links = [
        link.get("href") for link in soup.find_all("link", {"rel": "stylesheet"})
    ]

    favicon = None
    for link in soup.find_all("link", {"rel": "icon"}):
        favicon = link.get("href", "")
        break

    colors_and_fonts = extract_colors_and_fonts(styles, css_links)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that extracts structured data from website HTML content.",
        },
        {
            "role": "user",
            "content": f"""
            Extract the following details from the given website information:
            1. brand_name
            2. brand_category (as array)
            3. brand_description (minimum 3 lines)
            4. brand_logo (URL or description)
            5. brand_colors (as CSS color codes in hex format)
            6. brand_fonts (valid font names)
            7. favicon (URL or description)

            Website Information:
            {preprocessed_content}

            Format the output in JSON. Include the extracted colors and fonts as well.
            """,
        },
    ]

    chat_response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )

    response = chat_response.choices[0].message.content
    response = response.replace("```json", "")
    response = response.replace("```", "")

    # Don't forget to convert to JSON as it is a string right now:
    json_result = json.loads(response)
    print(json_result)

    return json_result
