import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from telegram import Bot
import os
import asyncio

# Configuration
WEBSITE_URL = "http://renshi.people.com.cn/"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATA_FILE = "headlines.json"

def load_previous_headlines():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_headlines(headlines):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(headlines, f, ensure_ascii=False, indent=2)

def scrape_headlines():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        response = requests.get(WEBSITE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Select all news links starting with /n1/
        headline_links = soup.select('a[href^="/n1/"]')
        
        headlines = []
        for link in headline_links:
            title = link.get_text().strip()
            if title:  # Only include non-empty titles
                full_url = f"http://renshi.people.com.cn{link['href']}"
                headlines.append(f"{title} ({full_url})")
        
        print(f"Debug: Found {len(headlines)} news headlines")
        return headlines
    
    except Exception as e:
        print(f"Error scraping headlines: {str(e)}")
        return []

async def send_telegram_notification(headlines):
    try:
        if not headlines:
            await send_telegram_notification(["⚠️ 今日没有抓取到任何新闻标题"])
            return
            
        bot = Bot(token=TELEGRAM_TOKEN)
        message = "人民网人事频道最新新闻:\n\n" + "\n".join(f"• {h}" for h in headlines[:10])
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending Telegram message: {str(e)}")

def main():
    # Scrape new headlines
    new_headlines = scrape_headlines()
    
    # Load previous data
    previous_data = load_previous_headlines()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save new data
    if new_headlines:
        previous_data[today] = new_headlines
        save_headlines(previous_data)
    
    # Send notification
    asyncio.run(send_telegram_notification(new_headlines))

if __name__ == "__main__":
    main()