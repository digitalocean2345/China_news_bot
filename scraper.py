import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode # Import ParseMode for clarity
import os
import asyncio
from urllib.parse import urljoin
import logging
import html # For escaping titles

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Website URLs and Display Names
WEBSITES = {
    "人民网人事频道": "http://renshi.people.com.cn/",
    "PD Anti Corruption": "http://fanfu.people.com.cn/",
    "PD International Breaking News":"http://world.people.com.cn/GB/157278/index.html",
    "PD International In-depth":"http://world.people.com.cn/GB/14549/index.html",
    "PD Society":"http://society.people.com.cn/GB/136657/index.html",
    "PD Economy":"http://finance.people.com.cn/GB/70846/index.html",
    "Paper China Government":"https://www.thepaper.cn/list_25462",
    "Paper Personnel Trends":"https://www.thepaper.cn/list_25423",
    "Paper Tiger Hunt":"https://www.thepaper.cn/list_25490",
    "Paper Project No1":"https://www.thepaper.cn/list_25424",
    "Paper Zhongnanhai":"https://www.thepaper.cn/list_25488",
    "Paper Live on the scene":"https://www.thepaper.cn/list_25428",
    "Paper exclusive reports":"https://www.thepaper.cn/list_25427",
    "Paper public opinion":"https://www.thepaper.cn/list_25489"
}

# Environment Variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MS_TRANSLATOR_KEY = os.getenv('MS_TRANSLATOR_KEY')
MS_TRANSLATOR_REGION = os.getenv('MS_TRANSLATOR_REGION', 'global') # Use 'global' if not set

# Files and Limits
DATA_FILE = "headlines.json"
MAX_MESSAGE_LENGTH = 4000  # Telegram's limit is 4096, using 4000 for safety
REQUESTS_TIMEOUT = 20 # Timeout for website requests
TRANSLATOR_TIMEOUT = 10 # Timeout for translation requests
TRANSLATOR_API_VERSION = '3.0'

# CSS Selectors for finding headline links
SITE_SELECTORS = {
    "人民网人事频道": 'div.fl a[href*="/n1/"]', # Example: Find links within class 'fl' containing '/n1/'
    "PD Anti Corruption": 'div.fl a[href*="/n1/"]',     # Same selector for this site
    "PD International Breaking News": 'div.ej_bor a[href*="/n1/"]',
    "PD International In-depth": 'div.ej_bor a[href*="/n1/"]',
    "PD Society":'div.ej_list_box a[href*="/n1/"]',
    "PD Economy":'div.ej_list_box a[href*="/n1/"]',
    "Paper China Government": 'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper Personnel Trends": 'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper Tiger Hunt": 'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper Project No1":'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper Zhongnanhai":'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper Live on the scene":'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper exclusive reports":'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',
    "Paper public opinion":'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)',

}

# --- Helper Functions ---

def translate_text(text):
    """Translates text from Chinese (Simplified) to English using Microsoft Translator."""
    if not MS_TRANSLATOR_KEY:
        logging.warning("No Microsoft Translator key configured - returning original text.")
        return text
    if not text or text.isspace():
        logging.debug("Skipping translation for empty text.")
        return text

    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        'api-version': TRANSLATOR_API_VERSION,
        'from': 'zh-Hans',
        'to': 'en'
    }
    headers = {
        'Ocp-Apim-Subscription-Key': MS_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': MS_TRANSLATOR_REGION,
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]

    try:
        response = requests.post(endpoint, params=params, headers=headers, json=body, timeout=TRANSLATOR_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        translation_result = response.json()

        if translation_result and isinstance(translation_result, list) and 'translations' in translation_result[0]:
            translated_text = translation_result[0]['translations'][0]['text']
            logging.debug(f"Translated '{text[:30]}...' to '{translated_text[:30]}...'")
            return translated_text
        else:
            logging.error(f"Unexpected translation API response format for text: {text[:50]}...")
            return text # Return original on unexpected format

    except requests.exceptions.RequestException as e:
        logging.error(f"Translation network error: {e}")
        return text  # Return original text if translation fails
    except (KeyError, IndexError, Exception) as e:
        logging.error(f"Translation processing error: {e}")
        return text # Return original text on other errors

def load_previous_data():
    """Loads previously processed data (URLs, headlines) from the JSON file."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure processed_urls is a list (convert if necessary from older format)
            if "processed_urls" not in data or not isinstance(data["processed_urls"], list):
                 data["processed_urls"] = []
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Could not load data file ({e}), starting fresh.")
        return {"last_run": "", "processed_urls": [], "headlines": {}}

def save_data(data):
    """Saves the current state (processed URLs, headlines) to the JSON file."""
    try:
        # Convert set back to list for JSON serialization if needed
        if isinstance(data.get("processed_urls"), set):
             data["processed_urls"] = sorted(list(data["processed_urls"])) # Sort for consistency

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data saved successfully to {DATA_FILE}")
    except IOError as e:
        logging.error(f"Error saving data to {DATA_FILE}: {e}")
    except TypeError as e:
         logging.error(f"Error serializing data for saving: {e}")


def scrape_site(site_name, url, processed_urls_set):
    """Scrapes a single website for new headlines."""
    new_headlines = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' # Prefer English, accept Chinese
        }

        logging.info(f"Scraping: {site_name} ({url})")
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
        response.encoding = response.apparent_encoding # Try to guess encoding if not utf-8
        response.raise_for_status() # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        selector = SITE_SELECTORS.get(site_name)
        if not selector:
            logging.error(f"No selector defined for site: {site_name}")
            return []

        links = soup.select(selector)
        logging.info(f"Found {len(links)} potential links using selector '{selector}'")

        for link in links:
            chinese_title = link.get_text().strip()
            href = link.get('href', '')

            if not chinese_title or not href:
                logging.debug(f"Skipping link with missing title or href: {link}")
                continue

            # Resolve relative URLs to absolute URLs
            full_url = urljoin(url, href)

            # Check if URL has already been processed
            if full_url not in processed_urls_set:
                logging.info(f"Found new item: {chinese_title[:50]}... ({full_url})")
                english_title = translate_text(chinese_title)

                # Escape titles for HTML safety in Telegram message
                safe_english_title = html.escape(english_title)
                safe_chinese_title = html.escape(chinese_title)

                new_headlines.append({
                    "chinese_title": safe_chinese_title,
                    "english_title": safe_english_title,
                    "url": full_url,
                    "source": site_name, # Keep track of the source
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                processed_urls_set.add(full_url) # Add to the set of processed URLs
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
        logging.error(f"Unexpected error scraping {site_name} ({url}): {e}", exc_info=True) # Log traceback
        return []

async def send_telegram_messages(bot, chat_id, messages):
    """Sends a list of messages to Telegram, handling potential errors."""
    if not messages:
        logging.info("No messages to send.")
        return

    for i, message in enumerate(messages, 1):
        if not message or message.isspace():
            logging.warning(f"Skipping empty message part {i}/{len(messages)}.")
            continue
        try:
            logging.info(f"Sending message part {i}/{len(messages)} ({len(message)} chars)")
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logging.debug(f"Successfully sent message part {i}")
            # Add a small delay between messages if sending many parts
            if len(messages) > 1:
                await asyncio.sleep(0.5) # 0.5 second delay

        except telegram.error.BadRequest as e:
             logging.error(f"Telegram Bad Request error sending part {i}: {e}. Message length: {len(message)}")
             logging.debug(f"Failed message content (first 500 chars): {message[:500]}")
        except telegram.error.TelegramError as e:
            logging.error(f"Telegram API error sending part {i}: {e}")
            # Implement retry logic here if needed
            await asyncio.sleep(2) # Wait before potentially trying next part
        except Exception as e:
            logging.error(f"Unexpected error sending Telegram message part {i}: {e}", exc_info=True)

async def prepare_telegram_messages(items_by_site):
    """Prepares messages grouped by site, split to fit Telegram's limits."""
    if not items_by_site:
        logging.info("No new items found across all sites.")
        return ["ℹ️ No new content found today."]

    messages = []
    current_message = ""
    site_needs_continuation_header = {} # Track if a site got split {site_name: True}

    for site_name, items in items_by_site.items():
        if not items: # Skip sites with no new items
            continue

        # Determine header: Base or Continuation
        header_base = f"<b>📰 Updates from {site_name}</b>\n\n"
        header_cont = f"<b>📰 Updates from {site_name} (cont.)</b>\n\n"

        # Decide if we need the continuation header for *this* site
        is_continuation = site_needs_continuation_header.get(site_name, False)
        site_header = header_cont if is_continuation else header_base

        # Check if the header *itself* fits in a new message (edge case)
        if len(site_header) > MAX_MESSAGE_LENGTH:
            logging.warning(f"Site header for '{site_name}' is too long ({len(site_header)} chars). Skipping site.")
            continue

        # Check if adding the header to the current message exceeds the limit
        if current_message and len(current_message) + len(site_header) > MAX_MESSAGE_LENGTH:
            messages.append(current_message) # Finalize previous message
            current_message = site_header # Start new message with header
            # Reset continuation flags for other sites if we start a new message
            site_needs_continuation_header = {site_name: False} # This site starts fresh in new msg
        else:
            # Add header (either to empty message or existing one)
            if not current_message:
                current_message = site_header
            else:
                current_message += "\n" + site_header # Add separator before new section
            site_needs_continuation_header[site_name] = False # Added header normally

        # Add items for this site
        for item in items:
            item_text = (
                f"• <b>{item['english_title']}</b>\n"
                f"  ({item['chinese_title']})\n"
                f"  <a href='{item['url']}'>Read more</a>\n\n"
            )

            # Check if item_text itself is too large (should be rare)
            if len(item_text) > MAX_MESSAGE_LENGTH:
                 logging.warning(f"Single item too long ({len(item_text)} chars), skipping: {item['url']}")
                 continue # Skip this item

            # Check if adding this item exceeds the limit
            if len(current_message) + len(item_text) > MAX_MESSAGE_LENGTH:
                # Finish the current message
                messages.append(current_message)
                # Start a new message with a continuation header for *this site*
                current_message = header_cont + item_text
                # Mark that *this site* needs continuation header if more items follow
                site_needs_continuation_header[site_name] = True
                 # Reset continuation flags for other sites
                for other_site in site_needs_continuation_header:
                     if other_site != site_name:
                         site_needs_continuation_header[other_site] = False

                # Check edge case: continuation header + item is still too long
                if len(current_message) > MAX_MESSAGE_LENGTH:
                    logging.warning(f"Item too long even with continuation header ({len(current_message)} chars). Sending header and item separately for {item['url']}")
                    messages.append(header_cont) # Send just the header
                    # Attempt to send item alone (might still fail if item_text > limit)
                    if len(item_text) <= MAX_MESSAGE_LENGTH:
                         messages.append(item_text)
                    else:
                         logging.error(f"Cannot send item as it exceeds max length: {item['url']}")
                    current_message = "" # Reset message buffer
                    # Keep site_needs_continuation_header[site_name] = True

            else:
                # It fits, add it
                current_message += item_text

    # Add the last remaining message if it's not empty
    if current_message.strip():
        messages.append(current_message)

    if not messages: # If all items were skipped or sites empty
         logging.info("Prepared messages list is empty after processing items.")
         return ["ℹ️ No new content found today that could be formatted."]

    logging.info(f"Prepared {len(messages)} message parts for Telegram.")
    return messages


async def main_async():
    """Main asynchronous function to run the scraper and notifier."""
    # --- Essential Credential Check ---
    if not TELEGRAM_TOKEN:
        logging.critical("TELEGRAM_TOKEN environment variable not set. Exiting.")
        return
    if not TELEGRAM_CHAT_ID:
        logging.critical("TELEGRAM_CHAT_ID environment variable not set. Exiting.")
        return

    # --- Translator Key Check (Warning only) ---
    if not MS_TRANSLATOR_KEY:
        logging.warning("MS_TRANSLATOR_KEY not set. Headlines will not be translated.")

    # --- Initialize Bot ---
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.get_me() # Verify token validity
        logging.info("Telegram Bot initialized successfully.")
    except telegram.error.InvalidToken:
        logging.critical("Invalid TELEGRAM_TOKEN. Exiting.")
        return
    except Exception as e:
        logging.critical(f"Failed to initialize Telegram bot: {e}", exc_info=True)
        return

    # --- Load Data and Scrape ---
    data = load_previous_data()
    # Use a set for efficient URL checking during scraping
    processed_urls_set = set(data.get("processed_urls", []))
    all_new_items_by_site = {} # Store results grouped by site name

    for name, url in WEBSITES.items():
        new_items = scrape_site(name, url, processed_urls_set)
        if new_items:
            all_new_items_by_site[name] = new_items

    # --- Process and Send Results ---
    if all_new_items_by_site:
        logging.info(f"Found new items from {len(all_new_items_by_site)} sites.")

        # Flatten the items for saving historical data (optional, could save grouped too)
        flat_new_items = [item for items in all_new_items_by_site.values() for item in items]

        # Update data for saving
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str not in data["headlines"]:
             data["headlines"][today_str] = []
        data["headlines"][today_str].extend(flat_new_items) # Append new items for the day
        data["processed_urls"] = sorted(list(processed_urls_set)) # Update processed URLs list
        data["last_run"] = datetime.now().isoformat()
        save_data(data)

        # Prepare and send messages
        logging.info(f"Preparing {len(flat_new_items)} total updates for Telegram...")
        messages_to_send = await prepare_telegram_messages(all_new_items_by_site)
        await send_telegram_messages(bot, TELEGRAM_CHAT_ID, messages_to_send)

    else:
        logging.info("No new items found across all websites.")
        # Optionally send a "no updates" message
        # await send_telegram_messages(bot, TELEGRAM_CHAT_ID, ["ℹ️ No new content found today."])
        # Update last run time even if no news
        data["last_run"] = datetime.now().isoformat()
        # Save data even if no new headlines, to update last_run and processed_urls
        data["processed_urls"] = sorted(list(processed_urls_set))
        save_data(data)

    logging.info("Script finished.")

def main():
    """Synchronous entry point."""
    try:
        asyncio.run(main_async())
    except Exception as e:
        logging.critical(f"An unhandled error occurred in main: {e}", exc_info=True)

if __name__ == "__main__":
    # Ensure required packages are installed:
    # pip install python-telegram-bot~=20.0 requests beautifulsoup4 # Use ~=20.0 for compatibility with this async code
    # Or if using a newer version (e.g., 21+): pip install python-telegram-bot requests beautifulsoup4
    main()