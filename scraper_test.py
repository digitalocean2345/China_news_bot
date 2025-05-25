# scraper_test.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import html
from datetime import datetime

# Assuming these exist and are configured correctly
# from config import REQUESTS_TIMEOUT # Using a default if not imported
REQUESTS_TIMEOUT = 15 # Example value

# from translator import translate_text # Using a dummy for testing if needed
def translate_text(text): return f"[Translated] {text}" # Dummy function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Test parameters ---
target_url = "http://www.mod.gov.cn/gfbw/xwfyr/ztjzh/index.html"
#target_selector =  'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)'
target_selector = 'li a'
site_name_for_logging = "Test" # Added for logging clarity
# ----------------------

def scrape_site(url, selector, site_name):
    """Scrapes a single website for new headlines."""
    new_headlines = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }

        logging.info(f"Scraping: ({url})")
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
        # Use apparent_encoding for potentially better guessing on non-UTF8 sites
        response.encoding = response.apparent_encoding
        response.raise_for_status() # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.select(selector)
        logging.info(f"Found {len(links)} potential links using selector '{selector}' for {url}")

        for link in links:
            chinese_title = link.get_text().strip()
            href = link.get('href', '')

            if not chinese_title or not href:
                logging.debug(f"Skipping link with missing title or href in {link.prettify()[:100]}...")
                continue

            # Resolve relative URLs to absolute URLs
            full_url = urljoin(url, href)

            # Basic URL validation (optional)
            if not full_url.startswith(('http://', 'https://')):
                 logging.warning(f"Skipping invalid looking URL in {site_name}: {full_url}")
                 continue

            new_headlines.append({
                    "chinese_title": chinese_title,
                    "url": full_url,
                })
        logging.info(f"Finished scraping. Found {len(new_headlines)} new headlines.")
        return new_headlines

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error scraping ({url})")
        return []
    except requests.exceptions.HTTPError as e:
         logging.error(f"HTTP error scraping  ({url}): {e.response.status_code} {e.response.reason}")
         return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error scraping  ({url}): {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error scraping({url}): {e}", exc_info=True) # Log traceback
        return []





'''
##===========for guancha=====================

def extract_site_data(url, selector, site_name):
    """Attempts to scrape and extract headline data for Huanqiu editorial."""
    extracted_data = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }

        logging.info(f"Scraping: {site_name} ({url})")
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)

        # Optional: print raw HTML only if needed for deep debugging
        # print(response.text)

        response.encoding = response.apparent_encoding
        response.raise_for_status() # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        data_items = soup.select(selector)
        # Corrected logging: uses function's 'selector' and 'site_name', placed before return
        logging.info(f"Found {len(data_items)} potential data items using selector '{selector}' for {site_name}")

        processed_urls_set = set() # Simulate the processed set for testing duplicates if needed

        for item in data_items:
            
            # Extract Article ID
            aid_element = item.select_one('textarea.item-aid')
            article_id = aid_element.get_text(strip=True) if aid_element else None

            # Extract Title
            title_element = item.select_one('textarea.item-title')
            chinese_title = title_element.get_text(strip=True) if title_element else None

            if not article_id or not chinese_title:
                logging.warning(f"Skipping item in {site_name}, missing aid or title.")
                continue

            # Construct the URL
            relative_url = f"/article/{article_id}"
            full_url = urljoin(url, relative_url) # Use base 'url' passed to function

            # --- Mimic processing from original scraper ---
            if full_url not in processed_urls_set:
                logging.info(f"Found new item: {chinese_title[:50]}... ({full_url})")
                english_title = translate_text(chinese_title)

                # Escape for safety (though not strictly needed for console print)
                safe_english_title = html.escape(english_title)
                safe_chinese_title = html.escape(chinese_title)

                extracted_data.append({
                    "chinese_title": safe_chinese_title,
                    "english_title": safe_english_title,
                    "url": full_url,
                })
                processed_urls_set.add(full_url)
            else:
                logging.info(f"Skipping already processed URL: {full_url}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during scraping {site_name}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during scraping {site_name}: {e}", exc_info=True) # Log traceback

    return extracted_data
'''
# --- Execute the test ---
#extracted_headlines = extract_site_data(target_url, target_selector, site_name_for_logging)

extracted_headlines = scrape_site(target_url,target_selector, site_name_for_logging)
# --- Print the results ---
print("\n--- Extraction Results ---")
if extracted_headlines:
    for i, headline in enumerate(extracted_headlines):
        print(f"Headline {i+1}:")
        # Use html.unescape to make titles readable in console if needed
        print(f"  Title (CN): {html.unescape(headline['chinese_title'])}")
        #print(f"  Title (EN): {html.unescape(headline['english_title'])}")
        print(f"  URL: {headline['url']}")
        print("-" * 20)
    print(f"Total extracted: {len(extracted_headlines)}")
else:
    print("No headlines were extracted successfully.")
print("--- Test Finished ---")