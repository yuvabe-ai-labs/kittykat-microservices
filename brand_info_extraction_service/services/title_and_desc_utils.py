from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

def parse_meta_description(soup):
    # Check for <meta> tags with name="description" or property="og:description"
    description_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if description_meta and description_meta.get('content'):
        return description_meta['content']

    # Fallback: Extract visible text from <p> tags
    paragraphs = soup.find_all('p')
    visible_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    if visible_texts:
        return " | ".join(visible_texts[:2])  # Combine the first two paragraphs

    return None

async def extract_title_desc(url):
    """
    Extracts the title and description from a website after rendering its dynamic content.

    :param url: The URL of the website
    :return: A tuple containing the page title and description
    """
    async with async_playwright() as p:
        # Launch a headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        )
        page = await context.new_page()

        # Navigate to the URL
        await page.goto(url)

        # Wait for the page to load completely
        await page.wait_for_load_state("domcontentloaded")

        # Get the page content
        html_content = await page.content()

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the title
        title_tag = soup.find('title')
        page_title = title_tag.get_text() if title_tag else "No title found"

        # Extract the description
        page_description = parse_meta_description(soup) or "No description found"

        # Close the browser
        await browser.close()

        return page_title, page_description

# # Example usage
# url = "https://eu.venchi.com/"  # Replace with your URL
# title, description = asyncio.run(extract_title_desc(url))
# print("Page Title:", title)
# print("Page Description:", description)
