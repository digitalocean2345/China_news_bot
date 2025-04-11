import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import telegram
import os

# Configuration
WEBSITE_URL = "http://renshi.people.com.cn/"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATA_FILE = "headlines.json"

def load_previous_headlines():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_headlines(headlines):
    with open(DATA_FILE, 'w') as f:
        json.dump(headlines, f, ensure_ascii=False, indent=2)

def scrape_headlines():
    response = requests.get(WEBSITE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Adjust this selector based on actual page inspection
    headlines = [h.text.strip() for h in soup.select('.hdNews li a')]
    return headlines

def send_telegram_notification(headlines):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = "今日头条:\n\n" + "\n".join(f"• {h}" for h in headlines[:10])
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def main():
    # Scrape new headlines
    new_headlines = scrape_headlines()
    
    # Load previous data
    previous_data = load_previous_headlines()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save new data
    previous_data[today] = new_headlines
    save_headlines(previous_data)
    
    # Send notification
    send_telegram_notification(new_headlines)

if __name__ == "__main__":
    main()