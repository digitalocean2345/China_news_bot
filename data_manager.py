# data_manager.py
import json
import logging
from config import DATA_FILE
import os
from datetime import datetime

def load_previous_data():
    """Load previous headlines data, creating file if it doesn't exist"""
    empty_data = {
        "headlines": {},
        "processed_urls": set(),
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        if os.path.exists('headlines.json'):
            with open('headlines.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert processed_urls to set
                processed_urls = set(data.get('processed_urls', []))
                logging.info(f"Loaded {len(processed_urls)} processed URLs from headlines.json")
                data['processed_urls'] = processed_urls
                return data
    except Exception as e:
        logging.error(f"Error loading headlines.json: {e}")
    
    logging.warning("No existing headlines.json found or error loading it. Starting fresh.")
    return empty_data

def save_data(data):
    """Save headlines data with proper formatting"""
    try:
        # Ensure processed_urls is a list for JSON serialization
        if isinstance(data.get('processed_urls'), set):
            data['processed_urls'] = list(data['processed_urls'])
        
        # Count URLs before saving
        url_count = len(data['processed_urls'])
        
        with open('headlines.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved headlines.json with {url_count} processed URLs")
        
        # Convert back to set for continued use
        data['processed_urls'] = set(data['processed_urls'])
        
    except Exception as e:
        logging.error(f"Error saving headlines.json: {e}")