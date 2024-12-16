import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup

async def extract_favicon_url(url):
    """
    Extracts the favicon URL of a website asynchronously using Playwright.

    :param url: The URL of the website
    :return: The favicon URL if found, otherwise None
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
        page_source = await page.content()

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Try to find the favicon link in the <head> section
        favicon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())

        # Extract the href attribute if the tag is found
        if favicon_tag and 'href' in favicon_tag.attrs:
            favicon_url = favicon_tag['href']
            # Convert relative URLs to absolute URLs
            if not favicon_url.startswith('http'):
                favicon_url = urljoin(url, favicon_url)
            return favicon_url

        return None  # Favicon not found

# Example usage:
# url = "https://venchi.com/"
# favicon_url = asyncio.run(extract_favicon_url(url))
# print("Favicon URL:", favicon_url if favicon_url else "Not found")
