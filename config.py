# config.py
import os
import logging

# --- Logging Configuration ---
# Basic config can be set here or in main.py
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Environment Variables ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MS_TRANSLATOR_KEY = os.getenv('MS_TRANSLATOR_KEY')
MS_TRANSLATOR_REGION = os.getenv('MS_TRANSLATOR_REGION', 'global')

# --- File Paths and Limits ---
DATA_FILE = "headlines.json"
MAX_MESSAGE_LENGTH = 4000  # Telegram's limit is 4096
REQUESTS_TIMEOUT = 20 # Timeout for website requests
TRANSLATOR_TIMEOUT = 10 # Timeout for translation requests
TRANSLATOR_API_VERSION = '3.0'

# --- Website Configuration ---
WEBSITES = {
    "人民网人事频道": "http://renshi.people.com.cn/",
    "PD Anti Corruption": "http://fanfu.people.com.cn/",
    "PD International Breaking News": "http://world.people.com.cn/GB/157278/index.html",
    "PD International In-depth": "http://world.people.com.cn/GB/14549/index.html",
    "PD Society": "http://society.people.com.cn/GB/136657/index.html",
    "PD Economy": "http://finance.people.com.cn/GB/70846/index.html",
    "Paper China Government": "https://www.thepaper.cn/list_25462",
    "Paper Personnel Trends": "https://www.thepaper.cn/list_25423",
    "Paper Tiger Hunt": "https://www.thepaper.cn/list_25490",
    "Paper Project No1": "https://www.thepaper.cn/list_25424",
    "Paper Zhongnanhai": "https://www.thepaper.cn/list_25488",
    "Paper Live on the scene": "https://www.thepaper.cn/list_25428",
    "Paper exclusive reports": "https://www.thepaper.cn/list_25427",
    "Paper public opinion": "https://www.thepaper.cn/list_25489",
    "Guancha International": "https://www.guancha.cn/GuoJi%C2%B7ZhanLue/list_1.shtml",
    "Guancha Chinese Diplomacy": "https://www.guancha.cn/ZhongGuoWaiJiao/list_1.shtml"
}

# --- CSS Selectors ---
# Grouped for readability
PD_RENMIN_SELECTOR = 'div.fl a[href*="/n1/"]'
PD_WORLD_SELECTOR = 'div.ej_bor a[href*="/n1/"]'
PD_SOC_ECO_SELECTOR = 'div.ej_list_box a[href*="/n1/"]'
PAPER_SELECTOR = 'a.index_inherit__A1ImK[target="_blank"]:not(.index_listcontentbot__92p4_ a)' # Common selector for The Paper
GUANCHA_SELECTOR = 'h4.module-title a'


SITE_SELECTORS = {
    "人民网人事频道": PD_RENMIN_SELECTOR,
    "PD Anti Corruption": PD_RENMIN_SELECTOR,
    "PD International Breaking News": PD_WORLD_SELECTOR,
    "PD International In-depth": PD_WORLD_SELECTOR,
    "PD Society": PD_SOC_ECO_SELECTOR,
    "PD Economy": PD_SOC_ECO_SELECTOR,
    "Paper China Government": PAPER_SELECTOR,
    "Paper Personnel Trends": PAPER_SELECTOR,
    "Paper Tiger Hunt": PAPER_SELECTOR,
    "Paper Project No1": PAPER_SELECTOR,
    "Paper Zhongnanhai": PAPER_SELECTOR,
    "Paper Live on the scene": PAPER_SELECTOR,
    "Paper exclusive reports": PAPER_SELECTOR,
    "Paper public opinion": PAPER_SELECTOR,
    "Guancha International": GUANCHA_SELECTOR,
    "Guancha Chinese Diplomacy": GUANCHA_SELECTOR
}

# --- Validation (Optional but Recommended) ---
def validate_config():
    """Checks if essential configurations are set."""
    essential_vars = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        # Add MS_TRANSLATOR_KEY if translation is strictly required
    }
    missing = [name for name, value in essential_vars.items() if not value]
    if missing:
        logging.critical(f"Missing essential environment variables: {', '.join(missing)}")
        return False
    # Check if selectors exist for all websites
    missing_selectors = [name for name in WEBSITES if name not in SITE_SELECTORS]
    if missing_selectors:
         logging.critical(f"Missing selectors for websites: {', '.join(missing_selectors)}")
         return False
    return True