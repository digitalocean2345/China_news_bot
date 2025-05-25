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
    "Guancha Chinese Diplomacy": "https://www.guancha.cn/ZhongGuoWaiJiao/list_1.shtml",
    "GT China Politics": "https://www.globaltimes.cn/china/politics/index.html",
    "GT China Society": "https://www.globaltimes.cn/china/society/index.html",
    "GT China Diplomacy": "https://www.globaltimes.cn/china/diplomacy/index.html",
    "GT China Military": "https://www.globaltimes.cn/china/military/index.html",
    "GT China Science": "https://www.globaltimes.cn/china/science/index.html",
    "GT Source Voice": "https://www.globaltimes.cn/source/gt-voice/index.html",
    "GT Source Insight": "https://www.globaltimes.cn/source/insight/index.html",
    "GT Source Ecomony": "https://www.globaltimes.cn/source/economy/index.html",
    "GT Source Comments": "https://www.globaltimes.cn/source/comments/index.html",
    "GT Opinion Editorial": "https://www.globaltimes.cn/opinion/editorial/index.html",
    "GT Opinion Observer": "https://www.globaltimes.cn/opinion/observer/index.html",
    "GT Opinion Asian Review": "https://www.globaltimes.cn/opinion/asian-review/index.html",
    "GT Opinion Toptalk": "https://www.globaltimes.cn/opinion/top-talk/index.html",
    "GT Opinion Viewpoint": "https://www.globaltimes.cn/opinion/viewpoint/index.html",
    "GT Indepth":"https://www.globaltimes.cn/In-depth/index.html",
    "State Council News Releases": "https://www.gov.cn/lianbo/fabu/",
    "State Council Department News": "https://www.gov.cn/lianbo/bumen/",
    "State Council Local News": "https://www.gov.cn/lianbo/difang/",
    "State Council Government News Broadcast": "https://www.gov.cn/lianbo/",
    "State Council Breaking News": "https://www.gov.cn/toutiao/liebiao/",
    "State Council Latest Policies": "https://www.gov.cn/zhengce/zuixin/",
    "State Council Policy Interpretation": "https://www.gov.cn/zhengce/jiedu/",
    "NBS Data Release": "https://www.stats.gov.cn/sj/zxfb/",
    "NBS Data Interpretation": "https://www.stats.gov.cn/sj/sjjd/",
    "NBS Press Conference": "https://www.stats.gov.cn/sj/xwfbh/fbhwd/",
    "CAC":"https://www.cac.gov.cn/yaowen/wxyw/A093602index_1.htm",
    "Taiwan Affairs Office": "http://www.gwytb.gov.cn/xwdt/xwfb/wyly/",
    "Chinese Departments on Taiwan": "http://www.gwytb.gov.cn/bmst/",
    "MND Regular PC": "http://www.mod.gov.cn/gfbw/xwfyr/lxjzh_246940/index.html",
    "MND Routine PC": "http://www.mod.gov.cn/gfbw/xwfyr/yzxwfb/index.html",
    "MND Special PC": "http://www.mod.gov.cn/gfbw/xwfyr/ztjzh/index.html"

}
# ----------------ENGLISH_WEBSITES-------------------------------
ENGLISH_WEBSITES = ["GT China Politics",
                    "GT China Society",
                    "GT China Diplomacy",
                    "GT China Military",
                    "GT China Science",
                    "GT Source Voice",
                    "GT Source Insight",
                    "GT Source Ecomony",
                    "GT Source Comments",
                    "GT Opinion Editorial",
                    "GT Opinion Observer",
                    "GT Opinion Asian Review",
                    "GT Opinion Toptalk",
                    "GT Opinion Viewpoint",
                    "GT Indepth"
                ] # Add the names of your English websites here

# --- CSS Selectors ---
# Grouped for readability
PD_RENMIN_SELECTOR = 'div.fl a[href*="/n1/"]'
PD_WORLD_SELECTOR = 'div.ej_bor a[href*="/n1/"]'
PD_SOC_ECO_SELECTOR = 'div.ej_list_box a[href*="/n1/"]'
PAPER_SELECTOR = 'div.small_toplink__GmZhY > a.index_inherit__A1ImK[target="_blank"]' # Common selector for The Paper
GUANCHA_SELECTOR = 'h4.module-title a'
GT_SELECTOR = 'a.new_title_ms,div.common_title a,a.new_title_ml'
SC_SELECTOR = 'div.news_box a'
NBS_SELECTOR = 'a.pc1200'
CAC_SELECTOR = 'div#loadingInfoPage a'
TAO_SELECTOR = 'ul.scdList a'
MND_SELECTOR = 'li a'

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
    "Guancha Chinese Diplomacy": GUANCHA_SELECTOR,
    "GT China Politics": GT_SELECTOR,
    "GT China Society": GT_SELECTOR,
    "GT China Diplomacy": GT_SELECTOR,
    "GT China Military": GT_SELECTOR,
    "GT China Science": GT_SELECTOR,
    "GT Source Voice": GT_SELECTOR,
    "GT Source Insight": GT_SELECTOR,
    "GT Source Ecomony": GT_SELECTOR,
    "GT Source Comments": GT_SELECTOR,
    "GT Opinion Editorial": GT_SELECTOR,
    "GT Opinion Observer": GT_SELECTOR,
    "GT Opinion Asian Review": GT_SELECTOR,
    "GT Opinion Toptalk": GT_SELECTOR,
    "GT Opinion Viewpoint": GT_SELECTOR,
    "GT Indepth":GT_SELECTOR,
    "State Council News Releases": SC_SELECTOR,
    "State Council Department News": SC_SELECTOR,
    "State Council Local News": SC_SELECTOR,
    "State Council Government News Broadcast": 'div.zwlb_title a',
    "State Council Breaking News": SC_SELECTOR,
    "State Council Latest Policies": SC_SELECTOR,
    "State Council Policy Interpretation": SC_SELECTOR,
    "NBS Data Release": NBS_SELECTOR,
    "NBS Data Interpretation": NBS_SELECTOR,
    "NBS Press Conference": NBS_SELECTOR,
    "CAC": CAC_SELECTOR,
    "Taiwan Affairs Office": TAO_SELECTOR,
    "Chinese Departments on Taiwan": TAO_SELECTOR,
    "MND Regular PC": MND_SELECTOR,
    "MND Routine PC": MND_SELECTOR,
    "MND Special PC": MND_SELECTOR
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

# Add this with your other configuration variables
GITHUB_AUTO_PUSH = True  # Set to False if you don't want automatic pushing