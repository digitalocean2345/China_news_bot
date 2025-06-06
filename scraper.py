# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import html
import config
from datetime import datetime

from config import ENGLISH_WEBSITES, SITE_SELECTORS, REQUESTS_TIMEOUT
from translator import translate_text # Import from our translator module

def scrape_site(site_name, url, processed_urls_set):
    """Scrapes a single website for new headlines."""
    new_headlines = []
    try:
        # Add debug logging for processed_urls_set
        logging.info(f"Starting scrape for {site_name} with {len(processed_urls_set)} processed URLs")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }

        logging.info(f"Scraping: {site_name} ({url})")
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
        # Use apparent_encoding for potentially better guessing on non-UTF8 sites
        response.encoding = response.apparent_encoding
        response.raise_for_status() # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        selector = SITE_SELECTORS.get(site_name)
        
        # --- Add this Debugging line ---
        #print(f"DEBUG: For site '{site_name}', selector type is {type(selector)}, value is: {selector}")
        # --- End Debugging line ---

        if not selector:
            logging.error(f"No selector defined for site: {site_name}")
            return []

        links = soup.select(selector)
        logging.info(f"Found {len(links)} potential links using selector '{selector}' for {site_name}")

        for link in links:
            chinese_title = link.get_text().strip()
            href = link.get('href', '')

            if not chinese_title or not href:
                logging.debug(f"Skipping link with missing title or href in {site_name}: {link.prettify()[:100]}...")
                continue

            # Resolve relative URLs to absolute URLs
            full_url = urljoin(url, href)

            # Basic URL validation (optional)
            if not full_url.startswith(('http://', 'https://')):
                 logging.warning(f"Skipping invalid looking URL in {site_name}: {full_url}")
                 continue

            # Debug logging for URL checking
            logging.debug(f"Checking URL: {full_url}")
            logging.debug(f"Is URL in processed set: {full_url in processed_urls_set}")

            # Check if URL has already been processed
            if full_url not in processed_urls_set:
                logging.info(f"New URL found: {full_url}")
                
                needs_translation = site_name not in config.ENGLISH_WEBSITES
                if needs_translation:
                    english_title = translate_text(chinese_title)
                else:
                    english_title = chinese_title

                #english_title = translate_text(chinese_title) # Use imported function

                # Escape titles for HTML safety in Telegram message
                safe_english_title = html.escape(english_title) if english_title else "[Translation Error]"
                safe_chinese_title = html.escape(chinese_title)

                new_headlines.append({
                    "chinese_title": safe_chinese_title,
                    "english_title": safe_english_title,
                    "url": full_url,
                    "source": site_name, # Keep track of the source
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                processed_urls_set.add(full_url) # Add to the set of processed URLs
                logging.info(f"Added new headline: {safe_english_title[:50]}...")
            else:
                logging.debug(f"Skipping already processed URL: {full_url}")

        logging.info(f"Finished scraping {site_name}. Found {len(new_headlines)} new headlines.")
        return new_headlines

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error scraping {site_name} ({url})")
        return []
    except requests.exceptions.HTTPError as e:
         logging.error(f"HTTP error scraping {site_name} ({url}): {e.response.status_code} {e.response.reason}")
         return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error scraping {site_name} ({url}): {e}")
        return []
    except Exception as e:
        logging.error(f"Error scraping {site_name}: {e}", exc_info=True)
        return []