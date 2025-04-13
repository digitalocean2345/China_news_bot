import requests
from bs4 import BeautifulSoup
import logging

# Configure basic logging (optional, but good practice)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Parameters ---
url_to_inspect = "https://opinion.huanqiu.com/editorial"
selector_to_check = '.csr_sketch_txt_3 .item' # Keep selector for optional check
REQUESTS_TIMEOUT = 15
# ------------------

print(f"--- Fetching and Prettifying HTML ---")
print(f"URL: {url_to_inspect}")
print("Purpose: Print the raw HTML source fetched by requests.get() in a readable format.")
print("------------------------------------")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

try:
    logging.info(f"Requesting URL: {url_to_inspect}")
    response = requests.get(url_to_inspect, headers=headers, timeout=REQUESTS_TIMEOUT)
    response.raise_for_status() # Check for HTTP errors
    logging.info(f"Request successful (Status: {response.status_code})")

    # Use apparent_encoding for potentially better guessing on non-UTF8 sites
    # This is important for BeautifulSoup to parse correctly before prettifying
    response.encoding = response.apparent_encoding
    logging.info(f"Using encoding: {response.encoding}")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Prettify the HTML ---
    # This adds indentation to the parsed HTML structure
    pretty_html = soup.prettify(encoding=response.encoding.lower()) # Specify encoding if needed
    # -------------------------

    # --- Print the Prettified HTML ---
    # Decode if prettify returns bytes, otherwise print directly if it returns str
    if isinstance(pretty_html, bytes):
         print("\n--- Prettified HTML Source (from requests.get) ---")
         # Use errors='ignore' or 'replace' if there are potential decoding issues
         print(pretty_html.decode(response.encoding.lower(), errors='replace'))
         print("--- End of Prettified HTML Source ---")
    else: # If prettify returns a string (depends on bs4 version/parser)
         print("\n--- Prettified HTML Source (from requests.get) ---")
         print(pretty_html)
         print("--- End of Prettified HTML Source ---")
    # ---------------------------------

    # Optional: Still count matches in the prettified source as a check
    # Re-parse the prettified string or use the original soup object
    elements_found = soup.select(selector_to_check) # Use original soup object
    match_count = len(elements_found)
    print(f"\nINFO: Found {match_count} element(s) matching selector '{selector_to_check}' within this source.")


except requests.exceptions.Timeout:
    logging.error(f"Timeout error requesting {url_to_inspect}")
    print(f"ERROR: Timeout occurred when requesting the URL.")
except requests.exceptions.HTTPError as e:
     logging.error(f"HTTP error requesting {url_to_inspect}: {e.response.status_code} {e.response.reason}")
     print(f"ERROR: HTTP error occurred - {e.response.status_code} {e.response.reason}")
except requests.exceptions.RequestException as e:
    logging.error(f"Network error requesting {url_to_inspect}: {e}")
    print(f"ERROR: Network error occurred - {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    print(f"ERROR: An unexpected error occurred: {e}")

print("\n--- Script Finished ---")