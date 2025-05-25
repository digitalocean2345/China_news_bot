import json
from datetime import datetime

def create_empty_data():
    initial_data = {
        "headlines": {},
        "processed_urls": [],
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("headlines.json", "w", encoding="utf-8") as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=2)
        print("Created new headlines.json with empty data structure")

if __name__ == "__main__":
    create_empty_data() 