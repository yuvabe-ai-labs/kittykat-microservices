import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
import re
import aiohttp

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

async def extract_brand_details(url):
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
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)


        # Wait for the page to load completely
        await page.wait_for_load_state("domcontentloaded")
        logger.debug("Page loaded successfully.")
        
        # Get the page content
        html_content = await page.content()

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')


        #color
        colors = []

        logos = set()  # Use a set to store unique logo URLs


        #--------------------------Colours extraction-----------------------#


        # Extract inline styles from the page
        logger.debug("Extracting inline styles from the <style> tags...")
        for style in soup.find_all('style'):
            colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', style.text))

        # Extract linked CSS files
        logger.debug("Extracting linked CSS files...")
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            css_url = link.get('href')
            if css_url:
                if not css_url.startswith('http'):
                    css_url = urljoin(url, css_url)
                try:
                    logger.debug(f"Fetching CSS from: {css_url}")
                    response = await page.context.request.get(css_url)
                    if response.status == 200:
                        css_text = await response.text()
                        colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', css_text))
                except Exception as e:
                    logger.error(f"Error fetching CSS file {css_url}: {e}")
                    pass

        # Extract inline styles from HTML elements
        logger.debug("Extracting inline styles from HTML elements...")
        for element in soup.find_all(style=True):
            colors.extend(re.findall(r'#[0-9a-fA-F]{3,6}', element['style']))

        # Count frequency of each color and return the 5 most common ones
        logger.info("Counting the most frequent colors...")
        most_common_colors = [color for color, _ in Counter(colors).most_common(5)]
        logger.info("color extraction completed successfully")



        #------------------------------logo extraction---------------------------------#


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

        # Method 3: Look for images inside common header/navigation containers
        logger.debug("Searching in header/navigation containers...")
        header_classes = [ 'logo','navigation','wrapper','header-logo','header__heading']
        for header_class in header_classes:
            containers = soup.find_all('div', class_=lambda x: x and header_class in x.lower())
            for container in containers:
                img_tag = container.find('img')
                if img_tag and img_tag.get('src'):
                    logos.add(img_tag.get('src'))
                    logger.debug(f"Found logo in container '{header_class}': {img_tag.get('src')}")

        # Method 4: Search for images wrapped in <a> tags (commonly for logos)
        logger.debug("Searching for images wrapped in <a> tags...")
        for link in soup.find_all('a'):
            img_tag = link.find('img')
            if img_tag and img_tag.get('src'):
                # Check if 'logo', 'brand', or 'icon' is in the alt or title of the image
                alt_text = img_tag.get('alt', '').lower()
                title_text = img_tag.get('title', '').lower()
                if 'logo' in alt_text or 'logo' in title_text or 'brand' in alt_text or 'icon' in alt_text:
                    logos.add(img_tag.get('src'))
                    logger.debug(f"Found logo inside <a>: {img_tag.get('src')}")


        # Method 4(i): Search for images wrapped in <a> tags (commonly for logos)
        logger.debug("Searching for images wrapped in <h1> tags...")
        for link in soup.find_all('h1'):
            img_tag = link.find('img')
            if img_tag and img_tag.get('src'):
                # Check if 'logo', 'brand', or 'icon' is in the alt or title of the image
                alt_text = img_tag.get('alt', '').lower()
                title_text = img_tag.get('title', '').lower()
                if 'logo' in alt_text or 'logo' in title_text or 'brand' in alt_text or 'icon' in alt_text:
                    logos.add(img_tag.get('src'))
                    logger.debug(f"Found logo inside <a>: {img_tag.get('src')}")

        # Method 5: Dynamically rendered images (multiple <img> tags)
        logger.debug("Checking for dynamically rendered images...")
        try:
            dynamic_images = await page.query_selector_all('img')
            for img_element in dynamic_images:
                src = await img_element.get_attribute('src')
                if src:
                    # Fetch alt or title attributes for additional logo validation
                    alt_text = await img_element.get_attribute('alt')
                    title_text = await img_element.get_attribute('title')
                    if 'logo' in (alt_text or '').lower() or 'logo' in (title_text or '').lower() or 'brand' in (alt_text or '').lower() or 'icon' in (alt_text or '').lower():
                        logos.add(src)
                        logger.debug(f"Found dynamically rendered logo: {src}")
        except Exception as e:
            logger.warning(f"Error fetching dynamically rendered logos: {e}")


        logger.info("Logo extraction completed successfully")
        

        #---------------------------------fonts extraction---------------------------------------#


        fonts = Counter()
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
            cleaned_fonts = Counter()
            for font, count in fonts.items():
                # Remove quotes, whitespace, and ignore invalid entries
                cleaned_font = font.replace('"', '').replace("'", "").strip()
                # Filter out non-font-family rules and malformed entries
                if cleaned_font and not re.search(r'[{}:@]', cleaned_font):  # Skip CSS rules and invalid entries
                    cleaned_fonts[cleaned_font] += count

            # Get the 5 most dominant fonts
            dominant_fonts = cleaned_fonts.most_common(5)

        logger.info(f"Top 5 dominant fonts: {dominant_fonts}")

        logger.info("Fonts extraction completed successfully")


        #----------------------------favicon extraction-----------------------------------------#


        # Try to find the favicon link in the <head> section
        logger.debug("Searching for favicon link...")
        favicon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())

        # Extract the href attribute if the tag is found
        if favicon_tag and 'href' in favicon_tag.attrs:
            favicon_url = favicon_tag['href']
            # Convert relative URLs to absolute URLs
            if not favicon_url.startswith('http'):
                favicon_url = urljoin(url, favicon_url)
            logger.info(f"Favicon URL found: {favicon_url}")

        else: 
            logger.warning("Favicon not found.")
            favicon_url= ""  # Favicon not found

        logger.info("Favicon extraction completed successfully")

        #------------------------title and Description------------------#

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

        return page_title, page_description, most_common_colors,logos,dominant_fonts,favicon_url

# Example usage
# if __name__ == "__main__":
#     url = "https://eu.venchi.com/"  # Replace with your URL
#     logger.info("Starting the extraction process...")
#     title, description ,colors,logos,fonts,favicon= asyncio.run(extract_brand_details(url))
#     logger.info(f"Page Title: {title}")
#     logger.info(f"Page Description: {description}")
#     logger.info(f"colors: {colors}")
#     logger.info(f"logos: {logos}")
#     logger.info(f"fonts: {fonts}")
#     logger.info(f"favicon: {favicon}")
