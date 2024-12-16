import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_meta_description(soup):
    logger.debug("Attempting to parse meta description.")
    # Check for <meta> tags with name="description" or property="og:description"
    description_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if description_meta and description_meta.get('content'):
        logger.info("Meta description found.")
        return description_meta['content']

    # Fallback: Extract visible text from <p> tags
    paragraphs = soup.find_all('p')
    visible_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    if visible_texts:
        logger.info("No meta description found, extracting text from <p> tags.")
        return " | ".join(visible_texts[:2])  # Combine the first two paragraphs

    logger.warning("No description found.")
    return None

async def extract_title_desc(url):
    """
    Extracts the title and description from a website after rendering its dynamic content.

    :param url: The URL of the website
    :return: A tuple containing the page title and description
    """
    logger.info(f"Starting extraction for URL: {url}")
    
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
        html_content = await page.content()

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the title
        title_tag = soup.find('title')
        page_title = title_tag.get_text() if title_tag else "No title found"
        logger.info(f"Page title extracted: {page_title}")

        # Extract the description
        page_description = parse_meta_description(soup) or "No description found"
        logger.info(f"Page description extracted: {page_description}")

        # Close the browser
        await browser.close()
        logger.debug("Browser closed.")

        return page_title, page_description

# Example usage
# if __name__ == "__main__":
#     url = "https://eu.venchi.com/"  # Replace with your URL
#     logger.info("Starting the extraction process...")
#     title, description = asyncio.run(extract_title_desc(url))
#     logger.info(f"Page Title: {title}")
#     logger.info(f"Page Description: {description}")
