# main.py
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.error import InvalidToken, TelegramError
import concurrent.futures # To manage the executor for synchronous tasks

# Import functions and config from our modules
import config
from data_manager import load_previous_data, save_data
from scraper import scrape_site
from notifier import prepare_telegram_messages, send_telegram_messages
from page_generator import PageGenerator
from git_manager import GitManager

# Configure logging (do this once at the entry point)
# Includes module name in the log format for better context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S' # Added date format
)

async def main_async():
    """Main asynchronous function to run the scraper and notifier."""
    logging.info("Starting scraper process...")

    # Load previous data and debug
    data = load_previous_data()
    processed_urls = data.get('processed_urls', set())
    logging.info(f"Loaded {len(processed_urls)} previously processed URLs")
    
    # Print first few URLs for verification
    sample_urls = list(processed_urls)[:5]
    logging.info("Sample of processed URLs:")
    for url in sample_urls:
        logging.info(f"  - {url}")

    # --- Validate Configuration ---
    if not config.validate_config():
         logging.critical("Configuration validation failed. Exiting.")
         return # Exit if essential config is missing

    # --- Translator Key Check (Warning only) ---
    if not config.MS_TRANSLATOR_KEY:
        logging.warning("MS_TRANSLATOR_KEY not set. Headlines will not be translated.")

    # --- Initialize Bot ---
    try:
        # Consider adding connection pool size if needed for high concurrency later
        bot = Bot(token=config.TELEGRAM_TOKEN)
        await bot.get_me() # Verify token validity by making a simple API call
        logging.info("Telegram Bot initialized successfully.")
    except InvalidToken:
        logging.critical("Invalid TELEGRAM_TOKEN. Exiting.")
        return
    except TelegramError as e:
         logging.critical(f"Failed to connect to Telegram API: {e}. Check token and network.")
         return
    except Exception as e:
        logging.critical(f"Failed to initialize Telegram bot: {e}", exc_info=True)
        return

    # --- Load Data and Scrape ---
    data = load_previous_data()
    # Ensure processed_urls is a set for efficient lookups during scraping
    processed_urls_set = set(data.get("processed_urls", []))
    all_new_items_by_site = {} # Store results grouped by site name {site_name: [item1, item2]}
    original_processed_count = len(processed_urls_set)

    # Get the current running event loop
    loop = asyncio.get_running_loop()
    tasks = [] # List to hold awaitable tasks/futures

    # Use loop.run_in_executor to run the synchronous scrape_site concurrently
    # Use a ThreadPoolExecutor to run blocking I/O (like requests) without blocking the event loop
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor: # Adjust max_workers as needed
        for name, url in config.WEBSITES.items():
            # Schedule the synchronous function 'scrape_site' to run in the executor
            # Pass arguments to scrape_site after the function itself
            # This returns an awaitable future
            future = loop.run_in_executor(
                executor,              # The executor to use (ThreadPoolExecutor is good for I/O)
                scrape_site,           # The synchronous function to run
                name,                  # Argument 1 for scrape_site
                url,                   # Argument 2 for scrape_site
                processed_urls_set     # Argument 3 for scrape_site (passed as reference, modifications within threads need care if not using thread-safe types, but set.add is generally safe)
            )
            tasks.append((name, future)) # Store site name with the future

        # Wait for all scraping tasks (futures) to complete
        logging.info(f"Scheduled {len(tasks)} scraping tasks using ThreadPoolExecutor...")
        # asyncio.gather can wait on the futures returned by run_in_executor
        results = await asyncio.gather(*(future for _, future in tasks), return_exceptions=True)
        logging.info("Scraping tasks finished.")

    # Process results from asyncio.gather
    for i, result in enumerate(results):
        name, _ = tasks[i] # Get the site name corresponding to the result index
        if isinstance(result, Exception):
            # Log exceptions that occurred within the scrape_site function executed in the thread
            logging.error(f"Scraping task for '{name}' generated an exception: {result}", exc_info=False) # Set exc_info=True for full traceback from thread if needed
        elif isinstance(result, list) and result: # Check if the result is a non-empty list
            all_new_items_by_site[name] = result
            logging.info(f"Successfully processed results for '{name}', found {len(result)} new items.")
        elif isinstance(result, list):
             logging.info(f"Successfully processed results for '{name}', found 0 new items.")
        else:
            # Should not happen if scrape_site always returns a list or raises Exception
             logging.warning(f"Unexpected result type ({type(result)}) for scraping task '{name}'.")

    newly_processed_count = len(processed_urls_set) - original_processed_count
    logging.info(f"Scraping complete. Added {newly_processed_count} new URLs to processed set (Total: {len(processed_urls_set)}).")


    # --- Process and Send Results ---
    if all_new_items_by_site:
        total_new_items = sum(len(items) for items in all_new_items_by_site.values())
        logging.info(f"Found {total_new_items} new items across {len(all_new_items_by_site)} sites.")

        # Flatten the items for saving historical data
        flat_new_items = [item for items in all_new_items_by_site.values() for item in items]

        # Update data structure for saving
        # Use current date - consider making timezone explicit if running globally
        # For Taipei Time (CST, UTC+8)
        taipei_time = datetime.now(datetime.now().astimezone().tzinfo) # Get local time with tzinfo
        # Alternatively, force UTC: datetime.now(datetime.timezone.utc)
        today_str = taipei_time.strftime("%Y-%m-%d")
        timestamp_str = taipei_time.isoformat()


        if today_str not in data.get("headlines", {}): # Safe access using .get
             data["headlines"] = data.get("headlines", {}) # Ensure headlines dict exists
             data["headlines"][today_str] = []

        # Append items found in this run to today's list
        data["headlines"][today_str].extend(flat_new_items)

        data["processed_urls"] = processed_urls_set # Pass the updated set (will be converted to list in save_data)
        data["last_run"] = timestamp_str
        save_data(data) # Save using the function from data_manager

        # Prepare and send messages
        logging.info(f"Preparing {total_new_items} total updates for Telegram...")
        messages_to_send = await prepare_telegram_messages(all_new_items_by_site) # Uses the grouped dictionary
        await send_telegram_messages(bot, config.TELEGRAM_CHAT_ID, messages_to_send)

        # Generate GitHub Pages
        try:
            page_generator = PageGenerator()
            page_generator.generate_pages(data)
            
            # Push changes if enabled
            if config.GITHUB_AUTO_PUSH:
                git_manager = GitManager()
                git_manager.push_changes()
            
        except Exception as e:
            logging.error(f"Failed to generate/push GitHub Pages: {e}", exc_info=True)

    else:
        logging.info("No new items found across all websites during this run.")
        # Update last run time and save processed URLs even if no news
        timestamp_str = datetime.now(datetime.now().astimezone().tzinfo).isoformat()
        data["last_run"] = timestamp_str
        data["processed_urls"] = processed_urls_set # Save updated set
        save_data(data)

    logging.info("Script finished.")


def main():
    """Synchronous entry point."""
    try:
        # Use asyncio.run() which handles the event loop lifecycle cleanly
        asyncio.run(main_async())
    except KeyboardInterrupt:
         logging.info("Script interrupted by user.")
         # Perform any necessary cleanup here if needed
    except Exception as e:
        # Catch any unexpected synchronous errors during setup or shutdown
        logging.critical(f"An unhandled error occurred in main synchronous execution: {e}", exc_info=True)
        # Optionally exit with a non-zero code
        # sys.exit(1)


if __name__ == "__main__":
    # Standard entry point guard
    main()