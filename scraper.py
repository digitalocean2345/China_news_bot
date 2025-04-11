import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from telegram import Bot
import os
import asyncio
from urllib.parse import urljoin
import sys
import io

# Set default encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
WEBSITES = {
    "人民网人事频道": "http://renshi.people.com.cn/",
    "反腐倡廉": "http://fanfu.people.com.cn/"
}

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATA_FILE = "headlines.json"

# Updated selectors for people.com.cn sites
SITE_SELECTORS = {
    "人民网人事频道": 'div.fl a[href*="/n1/"]',  # Updated selector
    "反腐倡廉": 'div.fl a[href*="/n1/"]',    # Updated selector
}

def load_previous_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "last_run": data.get("last_run", ""),
                "processed_urls": set(data.get("processed_urls", [])),
                "headlines": data.get("headlines", {})
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_run": "", "processed_urls": set(), "headlines": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "last_run": data["last_run"],
            "processed_urls": list(data["processed_urls"]),
            "headlines": data["headlines"]
        }, f, ensure_ascii=False, indent=2)

def scrape_site(site_name, url, processed_urls):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        print(f"Attempting to scrape: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        selector = SITE_SELECTORS.get(site_name, 'a[href*="/"]')
        print(f"Using selector: {selector}")
        
        links = soup.select(selector)
        print(f"Found {len(links)} potential links")
        
        new_headlines = []
        for link in links:
            title = link.get_text().strip()
            href = link.get('href', '')
            
            if not title or not href:
                continue
                
            full_url = urljoin(url, href)
            
            if full_url not in processed_urls:
                new_headlines.append({
                    "title": title,
                    "url": full_url,
                    "source": site_name,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                processed_urls.add(full_url)
                print(f"New headline found: {title}")
        
        print(f"Found {len(new_headlines)} new headlines from {site_name}")
        return new_headlines
    
    except Exception as e:
        print(f"Error scraping {site_name}: {str(e)}", file=sys.stderr)
        return []

async def send_telegram_notification(bot, news_items):
    try:
        if not news_items:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="ℹ️ 今日没有发现新的新闻")
            return
            
        # Group by source
        by_source = {}
        for item in news_items:
            by_source.setdefault(item["source"], []).append(item)
        
        # Format messages with HTML parsing
        for source, items in by_source.items():
            message = f"<b>{source}</b>\n\n"
            message += "\n".join(
                f'<a href="{item["url"]}">{item["title"]}</a>'
                for item in items
            )
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"Error sending Telegram message: {str(e)}", file=sys.stderr)

async def main_async():
    data = load_previous_data()
    all_new_items = []
    
    for site_name, url in WEBSITES.items():
        new_items = scrape_site(site_name, url, data["processed_urls"])
        all_new_items.extend(new_items)
        
        if site_name not in data["headlines"]:
            data["headlines"][site_name] = []
        data["headlines"][site_name].extend(new_items)
    
    data["last_run"] = datetime.now().isoformat()
    save_data(data)
    
    bot = Bot(token=TELEGRAM_TOKEN)
    await send_telegram_notification(bot, all_new_items)

def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram token or chat ID not set", file=sys.stderr)
        return
    
    asyncio.run(main_async())

if __name__ == "__main__":
    main()