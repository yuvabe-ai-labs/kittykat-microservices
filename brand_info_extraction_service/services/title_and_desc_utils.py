from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

def extract_title_desc(url):

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

    # Wait for the page to load
    time.sleep(5)

    # Extract page source
    html_content = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the title
    title_tag = soup.find('title')
    page_title = title_tag.get_text() if title_tag else "No title found"
    
    # Improved logic for extracting the description
    page_description = None

    # 1. Check for <meta> tags with name="description" or property="og:description"
    description_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if description_meta and description_meta.get('content'):
        page_description = description_meta['content']
    else:
        # 2. Fallback: Extract visible text from <p> tags (ignoring scripts, JSON, or dynamic content)
        paragraphs = soup.find_all('p')
        visible_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        if visible_texts:
            page_description = " | ".join(visible_texts[:2])  # Combine the first two non-empty paragraphs for context

    # Close the browser
    driver.quit()

    return page_title, page_description

# # Example usage
# url = "https://eu.venchi.com/"  # Replace with your URL
# title, description = extract_title_desc(url)

# print("Page Title:", title)
# print("Page Description:", description if description else "No description found.")
