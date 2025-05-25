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
                return json.load(f)
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
        # Convert processed_urls set to list if necessary
        if isinstance(data.get("processed_urls"), set):
            data["processed_urls"] = list(data["processed_urls"])
        
        # Save with proper formatting
        with open('headlines.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logging.info("Successfully saved headlines data")
    except Exception as e:
        logging.error(f"Error saving headlines.json: {e}")