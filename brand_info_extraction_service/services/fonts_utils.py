import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def extract_fonts(url):
    """
    Extract and clean fonts from a dynamically rendered webpage.
    :param url: The URL of the webpage
    :return: List of unique fonts in clean, formatted output
    """
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
        # Open the dynamic webpage
        driver.get(url)
        
        # Wait for the page to load dynamically rendered content
        driver.implicitly_wait(10)  # Wait up to 10 seconds for the page to load

        # Get the page source after the JavaScript has rendered the content
        page_source = driver.page_source

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract fonts using the original method
        fonts = set()
        font_pattern = re.compile(r'font-family\s*:\s*([^;]+)')  # Regex to find font-family

        # Extract fonts from inline <style> tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:  # Ensure there is CSS content in the tag
                matches = font_pattern.findall(style.string)
                for match in matches:
                    fonts.update([font.strip() for font in match.split(',')])

        # Extract fonts from external CSS files
        link_tags = soup.find_all('link', rel='stylesheet')
        for link in link_tags:
            css_url = link.get('href')
            if css_url:
                # Handle relative and absolute URLs
                css_url = css_url if css_url.startswith('http') else url + css_url
                try:
                    css_response = requests.get(css_url)
                    if css_response.status_code == 200:
                        matches = font_pattern.findall(css_response.text)
                        for match in matches:
                            fonts.update([font.strip() for font in match.split(',')])
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch CSS file: {css_url}. Error: {e}")

        # Clean and validate fonts
        cleaned_fonts = set()
        for font in fonts:
            # Remove quotes, whitespace, and ignore invalid entries
            cleaned_font = font.replace('"', '').replace("'", "").strip()
            # Filter out non-font-family rules and malformed entries
            if cleaned_font and not re.search(r'[{}:@]', cleaned_font):  # Skip CSS rules and invalid entries
                cleaned_fonts.add(cleaned_font)

        # Return the sorted list of cleaned fonts
        return sorted(cleaned_fonts)

    finally:
        driver.quit()

# # Example usage:
# url = 'https://www.a2dpcfactory.com/'  # Replace with the target URL
# fonts = extract_fonts(url)
# print(fonts)
