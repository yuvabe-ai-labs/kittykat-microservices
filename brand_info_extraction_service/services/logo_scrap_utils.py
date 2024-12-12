from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def extract_logos(url):

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

    # Wait for the page to fully load (adjust time if necessary)
    time.sleep(5)  # Adjust based on your page's loading time

    # Extract page source
    html_content = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    logos = set()  # Use a set to store unique logo URLs

    # Method 1: Directly find logo using alt text
    logo_tags = soup.find_all('img', alt=lambda x: x and 'logo' in x.lower())  # Filters alt text containing 'logo'
    if logo_tags:
        for logo in logo_tags:
            logo_src = logo.get('src')
            if logo_src:
                logos.add(logo_src)

    # Method 2: Handle nested <div> structures dynamically
    header_section = soup.find('div', class_=lambda x: x and 'headerSection' in x)  # Adjust based on the class in your HTML
    if header_section:
        logo_container = header_section.find('div', class_=lambda x: x and 'imageDiv' in x)  # Adjust further as needed
        if logo_container:
            nested_logo_img = logo_container.find('img')  # Target the <img> tag
            if nested_logo_img and nested_logo_img.get('src'):
                logos.add(nested_logo_img.get('src'))

    # Method 3: Selenium for dynamically rendered elements
    try:
        # Wait for the specific <img> element to load dynamically
        logo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'img'))
        )
        if logo_element:
            dynamic_logo_src = logo_element.get_attribute('src')
            logos.add(dynamic_logo_src)
    except Exception as e:
        pass  # If no dynamically rendered logo found, proceed

    # Close the browser
    driver.quit()

    return logos

# Example usage
# url = "https://venchi.com/"  # Replace with your URL
# logos = extract_logos(url)

# print("Found logos:")
# for logo in logos:
#     print(logo)
