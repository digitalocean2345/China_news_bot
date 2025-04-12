# data_manager.py
import json
import logging
from config import DATA_FILE

def load_previous_data():
    """Loads previously processed data (URLs, headlines) from the JSON file."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure processed_urls is a list
            if "processed_urls" not in data or not isinstance(data["processed_urls"], list):
                 data["processed_urls"] = []
            # Ensure headlines is a dict
            if "headlines" not in data or not isinstance(data["headlines"], dict):
                data["headlines"] = {}
            return data
    except FileNotFoundError:
        logging.warning(f"Data file '{DATA_FILE}' not found, starting fresh.")
        return {"last_run": "", "processed_urls": [], "headlines": {}}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{DATA_FILE}': {e}. Starting fresh.")
        # Consider backing up the corrupted file here if needed
        return {"last_run": "", "processed_urls": [], "headlines": {}}
    except Exception as e:
         logging.error(f"Unexpected error loading data from '{DATA_FILE}': {e}. Starting fresh.")
         return {"last_run": "", "processed_urls": [], "headlines": {}}


def save_data(data):
    """Saves the current state (processed URLs, headlines) to the JSON file."""
    if not isinstance(data.get("processed_urls"), (list, set)):
        logging.error("Invalid data format: 'processed_urls' is not a list or set. Aborting save.")
        return
    if not isinstance(data.get("headlines"), dict):
        logging.error("Invalid data format: 'headlines' is not a dictionary. Aborting save.")
        return

    try:
        # Convert set back to list for JSON serialization if needed
        if isinstance(data.get("processed_urls"), set):
             data["processed_urls"] = sorted(list(data["processed_urls"])) # Sort for consistency

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data saved successfully to {DATA_FILE}")
    except IOError as e:
        logging.error(f"Error saving data to {DATA_FILE}: {e}")
    except TypeError as e:
         logging.error(f"Error serializing data for saving: {e}")
    except Exception as e:
         logging.error(f"Unexpected error saving data to '{DATA_FILE}': {e}")