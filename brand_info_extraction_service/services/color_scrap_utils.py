from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
from collections import Counter
import requests
import time

def extract_dominant_colors(url):
    """
    Extracts the 5 most dominant colors from the website's inline styles and linked CSS files
    after rendering the dynamic content.

    :param url: The URL of the website
    :return: A list of the 5 most frequent colors (hex codes)
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
    driver.get(url)

    # Wait for the page to fully render (adjust time as needed)
    time.sleep(5)

    # Get the rendered HTML content
    html_content = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    colors = []

    # Extract inline styles from the page
    for style in soup.find_all('style'):
        colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', style.text))

    # Extract linked CSS files
    for link in soup.find_all('link', {'rel': 'stylesheet'}):
        css_url = link.get('href')
        if css_url:
            if not css_url.startswith('http'):
                css_url = requests.compat.urljoin(url, css_url)
            try:
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', css_response.text))
            except requests.RequestException:
                pass

    # Extract inline styles from HTML elements
    for element in soup.find_all(style=True):
        colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', element['style']))

    # Count frequency of each color and return the 5 most common ones
    most_common_colors = [color for color, _ in Counter(colors).most_common(5)]

    # Close the browser
    driver.quit()

    return most_common_colors

# # Example usage
# url = "https://eu.venchi.com/"  # Replace with your target URL
# dominant_colors = extract_dominant_colors(url)
# print("Dominant Colors:", dominant_colors)
