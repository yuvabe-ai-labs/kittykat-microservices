from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def extract_favicon_url(url):
    """
    Extracts the favicon URL of a website using Selenium.

    :param url: The URL of the website
    :return: The favicon URL if found, otherwise None
    """
    # Set up Selenium WebDriver with Chrome
    # Set up Selenium WebDriver with Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Open the website
        driver.get(url)

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Extract the page source
        page_source = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Try to find the favicon link in the <head> section
        favicon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())

        # Extract the href attribute if the tag is found
        if favicon_tag and 'href' in favicon_tag.attrs:
            favicon_url = favicon_tag['href']
            # Convert relative URLs to absolute URLs
            if not favicon_url.startswith('http'):
                from urllib.parse import urljoin
                favicon_url = urljoin(url, favicon_url)
            return favicon_url

        return None  # Favicon not found

    finally:
        driver.quit()

# Example usage:
# url = "https://example.com"
# favicon_url = extract_favicon_url(url)
# print("Favicon URL:", favicon_url if favicon_url else "Not found")
