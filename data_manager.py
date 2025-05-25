# data_manager.py
import json
import logging
from config import DATA_FILE
import os
from datetime import datetime

def load_previous_data():
    """Load previous headlines data, creating file if it doesn't exist"""
    try:
        if os.path.exists('headlines.json'):
            with open('headlines.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure processed_urls exists and is a set
                if 'processed_urls' not in data:
                    data['processed_urls'] = []
                # Convert to set for efficient lookups
                data['processed_urls'] = list(set(data['processed_urls']))
                return data
    except Exception as e:
        logging.error(f"Error loading headlines.json: {e}")
    
    # Return empty structure if file doesn't exist or has error
    return {
        "headlines": {},
        "processed_urls": [],
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def save_data(data):
    """Save headlines data with proper formatting"""
    try:
        # Ensure we're not duplicating processed URLs
        if isinstance(data.get("processed_urls"), (list, set)):
            data["processed_urls"] = list(set(data["processed_urls"]))
        
        # Save with proper formatting
        with open('headlines.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Successfully saved headlines data with {len(data['processed_urls'])} processed URLs")
    except Exception as e:
        logging.error(f"Error saving headlines.json: {e}")