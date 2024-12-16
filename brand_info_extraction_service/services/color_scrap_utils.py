import logging
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_dominant_colors(url):
    """
    Extracts the 5 most dominant colors from the website's inline styles and linked CSS files
    after rendering the dynamic content.

    :param url: The URL of the website
    :return: A list of the 5 most frequent colors (hex codes)
    """
    logger.info(f"Starting to extract dominant colors from: {url}")
    
    async with async_playwright() as p:
        # Launch a headless browser
        logger.debug("Launching headless browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        )
        page = await context.new_page()

        # Navigate to the URL
        logger.info(f"Navigating to URL: {url}")
        await page.goto(url)

        # Wait for the page to load completely
        await page.wait_for_load_state("domcontentloaded")
        logger.debug("Page loaded successfully.")

        # Get the page content
        page_source = await page.content()

        # Parse the HTML with BeautifulSoup
        logger.debug("Parsing page content with BeautifulSoup...")
        soup = BeautifulSoup(page_source, 'html.parser')

        colors = []

        # Extract inline styles from the page
        logger.debug("Extracting inline styles from the <style> tags...")
        for style in soup.find_all('style'):
            colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', style.text))

        # Extract linked CSS files
        logger.debug("Extracting linked CSS files...")
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            css_url = link.get('href')
            if css_url:
                if not css_url.startswith('http'):
                    css_url = urljoin(url, css_url)
                try:
                    logger.debug(f"Fetching CSS from: {css_url}")
                    response = await page.context.request.get(css_url)
                    if response.status == 200:
                        css_text = await response.text()
                        colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', css_text))
                except Exception as e:
                    logger.error(f"Error fetching CSS file {css_url}: {e}")
                    pass

        # Extract inline styles from HTML elements
        logger.debug("Extracting inline styles from HTML elements...")
        for element in soup.find_all(style=True):
            colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', element['style']))

        # Count frequency of each color and return the 5 most common ones
        logger.info("Counting the most frequent colors...")
        most_common_colors = [color for color, _ in Counter(colors).most_common(5)]

        # Close the browser
        await browser.close()

        logger.info(f"Dominant colors extracted: {most_common_colors}")
        return most_common_colors

# Example usage
# url = "https://eu.venchi.com/"  # Replace with your target URL
# dominant_colors = asyncio.run(extract_dominant_colors(url))
# print("Dominant Colors:", dominant_colors)
