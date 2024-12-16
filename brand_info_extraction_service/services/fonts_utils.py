import logging
import asyncio
from playwright.async_api import async_playwright
import re
import aiohttp
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fetch_css(session, css_url, url):
    """
    Fetch the content of a CSS file asynchronously.
    :param session: aiohttp session object
    :param css_url: URL of the CSS file
    :param url: The base URL to resolve relative links
    :return: CSS content as string
    """
    if not css_url.startswith('http'):
        css_url = url + css_url  # Handle relative URL

    try:
        logger.debug(f"Fetching CSS from: {css_url}")
        async with session.get(css_url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logger.warning(f"Failed to fetch CSS file: {css_url}, Status code: {response.status}")
    except Exception as e:
        logger.error(f"Error fetching CSS file {css_url}: {e}")
    return ''

async def extract_fonts(url):
    """
    Extract and clean fonts from a dynamically rendered webpage asynchronously.
    :param url: The URL of the webpage
    :return: List of unique fonts in clean, formatted output
    """
    logger.info(f"Starting font extraction from: {url}")

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

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        fonts = set()
        font_pattern = re.compile(r'font-family\s*:\s*([^;]+)')  # Regex to find font-family

        # Extract fonts from inline <style> tags
        logger.debug("Extracting fonts from <style> tags...")
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:  # Ensure there is CSS content in the tag
                matches = font_pattern.findall(style.string)
                for match in matches:
                    fonts.update([font.strip() for font in match.split(',')])

        # Extract fonts from external CSS files asynchronously
        logger.debug("Extracting fonts from external CSS files...")
        link_tags = soup.find_all('link', rel='stylesheet')
        async with aiohttp.ClientSession() as session:
            css_tasks = []
            for link in link_tags:
                css_url = link.get('href')
                if css_url:
                    logger.debug(f"Found external CSS file: {css_url}")
                    css_tasks.append(fetch_css(session, css_url, url))

            # Wait for all CSS files to be fetched asynchronously
            css_contents = await asyncio.gather(*css_tasks)

            # Extract fonts from each fetched CSS content
            for css_content in css_contents:
                if css_content:
                    matches = font_pattern.findall(css_content)
                    for match in matches:
                        fonts.update([font.strip() for font in match.split(',')])

        # Clean and validate fonts
        logger.debug("Cleaning and validating font names...")
        cleaned_fonts = set()
        for font in fonts:
            # Remove quotes, whitespace, and ignore invalid entries
            cleaned_font = font.replace('"', '').replace("'", "").strip()
            # Filter out non-font-family rules and malformed entries
            if cleaned_font and not re.search(r'[{}:@]', cleaned_font):  # Skip CSS rules and invalid entries
                cleaned_fonts.add(cleaned_font)

        # Close the browser
        await browser.close()
        logger.debug("Browser closed.")

        # Return the sorted list of cleaned fonts
        logger.info(f"Font extraction complete. Found {len(cleaned_fonts)} unique fonts.")
        return sorted(cleaned_fonts)

# Example usage:
# url = 'https://www.a2dpcfactory.com/'  # Replace with the target URL
# fonts = asyncio.run(extract_fonts(url))
# print(fonts)
