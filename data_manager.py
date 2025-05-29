# data_manager.py
import json
import logging
from config import DATA_FILE
import os
from datetime import datetime
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    """Normalize URL to ensure consistent comparison"""
    parsed = urlparse(url)
    # Normalize to lowercase
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/')  # Remove trailing slashes
    # Reconstruct URL with normalized components
    normalized = urlunparse((
        parsed.scheme.lower(),
        netloc,
        path,
        parsed.params,
        parsed.query,
        ''  # Remove fragments
    ))
    return normalized

def load_previous_data():
    """Load previous headlines data with URL normalization"""
    empty_data = {
        "headlines": {},
        "processed_urls": set(),
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        if os.path.exists('headlines.json'):
            with open('headlines.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert processed_urls to set with normalized URLs
                processed_urls = {normalize_url(url) for url in data.get('processed_urls', [])}
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
        # Ensure processed_urls contains normalized URLs and is converted to list for JSON
        if isinstance(data.get('processed_urls'), set):
            # Normalize all URLs before saving
            processed_urls = {normalize_url(url) for url in data['processed_urls']}
            data['processed_urls'] = list(processed_urls)
        
        # Count URLs before saving
        url_count = len(data['processed_urls'])
        
        with open('headlines.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved headlines.json with {url_count} processed URLs")
        
        # Convert back to set for continued use
        data['processed_urls'] = set(data['processed_urls'])
        
    except Exception as e:
        logging.error(f"Error saving headlines.json: {e}")

seen_urls = set()  # This will store normalized URLs
deduplicated_items_by_site = {}

def deduplicate_items(items):
    """Deduplicate items using normalized URLs"""
    unique_items = []
    
    for item in items:
        normalized_url = normalize_url(item['url'])
        logging.info(f"Processing URL: {item['url']}")
        logging.info(f"Normalized URL: {normalized_url}")
        
        if normalized_url not in seen_urls:
            seen_urls.add(normalized_url)
            unique_items.append(item)
            logging.info(f"Added new unique URL: {normalized_url}")
        else:
            logging.warning(f"Duplicate URL found and filtered: {item['url']} (normalized: {normalized_url})")
    
    return unique_items