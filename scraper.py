import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from telegram import Bot
import os
import asyncio
from urllib.parse import urljoin

# Configuration
WEBSITES = {
    "人民网人事频道": "http://renshi.people.com.cn/",
    "反腐倡廉": "http://fanfu.people.com.cn/"
}

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MS_TRANSLATOR_KEY = os.getenv('MS_TRANSLATOR_KEY')
DATA_FILE = "headlines.json"
MAX_MESSAGE_LENGTH = 4000  # Telegram's limit is 4096, we use 4000 for safety

# Selectors
SITE_SELECTORS = {
    "人民网人事频道": 'div.fl a[href*="/n1/"]',
    "反腐倡廉": 'div.fl a[href*="/n1/"]'
}

def translate_text(text):
    """Microsoft Translator API implementation"""
    if not MS_TRANSLATOR_KEY:
        print("Warning: No translator key configured - returning original text")
        return text
        
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        'api-version': '3.0',
        'from': 'zh-Hans',
        'to': 'en'
    }
    headers = {
        'Ocp-Apim-Subscription-Key': MS_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': 'global',
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]
    
    try:
        response = requests.post(endpoint, params=params, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        return response.json()[0]['translations'][0]['text']
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

def load_previous_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_run": "", "processed_urls": [], "headlines": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape_site(site_name, url, processed_urls):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        print(f"Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select(SITE_SELECTORS[site_name])
        
        new_headlines = []
        for link in links:
            chinese_title = link.get_text().strip()
            href = link.get('href', '')
            
            if not chinese_title or not href:
                continue
                
            full_url = urljoin(url, href)
            
            if full_url not in processed_urls:
                english_title = translate_text(chinese_title)
                new_headlines.append({
                    "chinese_title": chinese_title,
                    "english_title": english_title,
                    "url": full_url,
                    "source": site_name,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                processed_urls.append(full_url)
                print(f"New: {chinese_title[:30]}... → {english_title[:30]}...")
        
        print(f"Found {len(new_headlines)} new headlines from {site_name}")
        return new_headlines
        
    except Exception as e:
        print(f"Error scraping {site_name}: {str(e)}")
        return []

async def send_telegram_messages(bot, messages):
    """Send multiple Telegram messages with error handling"""
    for i, message in enumerate(messages, 1):
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            print(f"Sent message part {i}/{len(messages)}")
        except Exception as e:
            print(f"Failed to send message part {i}: {str(e)}")

async def prepare_telegram_messages(items):
    """Prepare messages split into chunks that fit Telegram's limits"""
    if not items:
        return ["ℹ️ No new content today"]
    
    messages = []
    current_message = "📰 Latest Personnel Updates\n\n"
    part_number = 1
    
    for item in items:
        item_text = (
            f"• <b>{item['english_title']}</b>\n"
            f"  ({item['chinese_title']})\n"
            f"  <a href='{item['url']}'>Read more</a>\n\n"
        )
        
        # If adding this item would exceed the limit
        if len(current_message) + len(item_text) > MAX_MESSAGE_LENGTH:
            messages.append(current_message)
            part_number += 1
            current_message = f"📰 Latest Personnel Updates (Part {part_number})\n\n"
        
        current_message += item_text
    
    if current_message.strip():
        messages.append(current_message)
    
    return messages

async def main_async():
    # Verify credentials
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Missing Telegram credentials")
        return
    
    if not MS_TRANSLATOR_KEY:
        print("Warning: No Microsoft Translator key configured - translations will be in Chinese")
    
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        print("Bot initialized successfully")
    except Exception as e:
        print(f"Failed to initialize bot: {str(e)}")
        return

    data = load_previous_data()
    processed_urls = data.get("processed_urls", [])
    all_new_items = []
    
    for name, url in WEBSITES.items():
        new_items = scrape_site(name, url, processed_urls)
        all_new_items.extend(new_items)
    
    if all_new_items:
        data["headlines"] = data.get("headlines", {})
        data["headlines"][datetime.now().strftime("%Y-%m-%d")] = all_new_items
        data["processed_urls"] = processed_urls
        save_data(data)
        
        print(f"Preparing {len(all_new_items)} updates for Telegram...")
        messages = await prepare_telegram_messages(all_new_items)
        print(f"Split into {len(messages)} message parts")
        await send_telegram_messages(bot, messages)
    else:
        print("No new items found")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    # Install required packages first:
    # pip install python-telegram-bot==20.0 requests==2.31.0 urllib3==1.26.18 beautifulsoup4
    main()