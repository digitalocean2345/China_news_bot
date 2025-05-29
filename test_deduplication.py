# test_deduplication.py
import logging
import asyncio
import time
from datetime import datetime
from data_manager import load_previous_data, save_data, deduplicate_items
from scraper import scrape_site
from notifier import prepare_telegram_messages
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def run_real_scrape_test(run_number):
    logging.info(f"\n=== Starting Real Scrape Test (Run #{run_number}) ===")
    
    # Load previous data
    data = load_previous_data()
    processed_urls = data.get('processed_urls', set())
    logging.info(f"Loaded {len(processed_urls)} previously processed URLs")

    # Store messages for comparison
    messages_this_run = []

    # Scrape all configured sites
    all_new_items_by_site = {}
    
    # Use all sites from config
    for name, url in config.WEBSITES.items():
        logging.info(f"\nScraping {name} from {url}")
        items = scrape_site(name, url, processed_urls)
        if items:
            all_new_items_by_site[name] = items
            logging.info(f"Found {len(items)} items from {name}")

    # Prepare telegram messages
    if all_new_items_by_site:
        messages = await prepare_telegram_messages(all_new_items_by_site)
        
        logging.info(f"\nMessages for Run #{run_number} that would be sent to Telegram:")
        for msg in messages:
            messages_this_run.append(msg)
            logging.info(f"\n---Message Content---\n{msg}\n---End Message---")
        
        # Update processed URLs and save
        for items in all_new_items_by_site.values():
            for item in items:
                processed_urls.add(item['url'])
        
        data['processed_urls'] = processed_urls
        save_data(data)
    else:
        logging.info(f"\nNo new items found to send to Telegram in Run #{run_number}")

    logging.info(f"=== Test Run #{run_number} Complete ===\n")
    return messages_this_run

if __name__ == "__main__":
    try:
        # Store messages from both runs
        logging.info("Starting first run...")
        first_run_messages = asyncio.run(run_real_scrape_test(1))
        
        if first_run_messages:
            logging.info(f"\nFound {len(first_run_messages)} messages in first run")
            logging.info("\nWaiting 15 minutes before second run...")
            time.sleep(900)  # Wait 15 minutes
            
            logging.info("\nStarting second run...")
            second_run_messages = asyncio.run(run_real_scrape_test(2))
            
            # Compare messages
            if second_run_messages:
                logging.info(f"\nFound {len(second_run_messages)} messages in second run")
                
                # Check for duplicates
                duplicates = []
                for msg1 in first_run_messages:
                    for msg2 in second_run_messages:
                        if msg1 == msg2:
                            duplicates.append(msg1)
                
                if duplicates:
                    logging.error(f"\nFound {len(duplicates)} duplicate messages between runs:")
                    for dup in duplicates:
                        logging.error(f"\n---Duplicate Message---\n{dup}\n---End Duplicate---")
                else:
                    logging.info("\nNo duplicate messages found between runs!")
            else:
                logging.info("\nNo messages in second run - deduplication working correctly!")
        else:
            logging.info("No messages found in first run - nothing to compare")
            
    except KeyboardInterrupt:
        logging.info("\nTest interrupted by user")
    except Exception as e:
        logging.error(f"Error during test: {e}", exc_info=True)