from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_logos(url):
    """
    Extracts logo URLs from a website after rendering its dynamic content.

    :param url: The URL of the website
    :return: A set of unique logo URLs
    """
    logger.info(f"Starting logo extraction for URL: {url}")

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

        logos = set()  # Use a set to store unique logo URLs

        # Method 1: Directly find logo using alt text
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        logo_tags = soup.find_all('img', alt=lambda x: x and 'logo' in x.lower())
        if logo_tags:
            logger.info(f"Found {len(logo_tags)} logos using 'alt' text.")
            for logo in logo_tags:
                logo_src = logo.get('src')
                if logo_src:
                    logos.add(logo_src)
                    logger.debug(f"Added logo URL: {logo_src}")

        # Method 2: Handle nested <div> structures dynamically
        header_section = soup.find('div', class_=lambda x: x and 'headerSection' in x)
        if header_section:
            logo_container = header_section.find('div', class_=lambda x: x and 'imageDiv' in x)
            if logo_container:
                nested_logo_img = logo_container.find('img')
                if nested_logo_img and nested_logo_img.get('src'):
                    logos.add(nested_logo_img.get('src'))
                    logger.debug(f"Added nested logo URL: {nested_logo_img.get('src')}")

        # Method 3: Dynamically rendered elements
        try:
            logger.info("Waiting for dynamically rendered logos...")
            dynamic_logo_element = await page.wait_for_selector('img', timeout=10000)  # Waits for any <img> element
            if dynamic_logo_element:
                dynamic_logo_src = await dynamic_logo_element.get_attribute('src')
                if dynamic_logo_src:
                    logos.add(dynamic_logo_src)
                    logger.debug(f"Added dynamically rendered logo URL: {dynamic_logo_src}")
        except Exception as e:
            logger.warning(f"No dynamically rendered logos found: {e}")

        try:
            logger.info("Searching for SVG logos...")
            svg_elements = soup.find_all('svg', class_=lambda x: x and 'icon' in x.lower())
            if svg_elements:
                logger.info(f"Found {len(svg_elements)} SVG logos.")
                for idx, svg in enumerate(svg_elements):
                    svg_content = str(svg)
                    logos.add(f"SVG_LOGO_{idx}")  # Placeholder for SVG logos
                    logger.debug(f"Extracted SVG content (truncated): {svg_content[:200]}...")

                    # (Optional) Save SVG content to a file
                    with open(f"logo_{idx}.svg", "w", encoding="utf-8") as file:
                        file.write(svg_content)
                        logger.debug(f"Saved SVG logo as 'logo_{idx}.svg'.")
        except Exception as e:
                logger.warning(f"Error in Method 4 (SVG elements): {e}")

        # Close the browser
        await browser.close()
        logger.debug("Browser closed.")

        logger.info(f"Logo extraction complete. Found {len(logos)} unique logos.")
        return logos

# Example usage
# if __name__ == "__main__":
#     url = "https://eu.venchi.com/"  # Replace with your URL
#     logger.info("Starting the logo extraction process...")
#     logos = asyncio.run(extract_logos(url))
#     logger.info(f"Extracted Logos: {logos}")
