import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil

class PageGenerator:
    def __init__(self, docs_dir='docs'):
        self.docs_dir = docs_dir
        self.template_dir = 'templates'
        
        # Create docs directory if it doesn't exist
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Copy static assets if they don't exist
        self.create_static_assets()
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def create_static_assets(self):
        """Create necessary static files if they don't exist"""
        # Create style.css
        css_file = os.path.join(self.docs_dir, 'style.css')
        if not os.path.exists(css_file):
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(self.get_css_content())
        
        # Create favicon
        favicon_file = os.path.join(self.docs_dir, 'favicon.ico')
        if not os.path.exists(favicon_file):
            # Create a simple favicon or copy from assets
            pass
    
    def generate_pages(self, data):
        """Generate HTML pages from the news data"""
        # Load the template
        template = self.env.get_template('index.html')
        
        # Prepare the data
        headlines = data.get("headlines", {})
        sorted_dates = sorted(headlines.keys(), reverse=True)
        
        news_by_date = []
        for date in sorted_dates:
            news_items = headlines[date]
            # Sort news items by their timestamp in reverse order
            news_items = sorted(news_items,
                              key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"),
                              reverse=True)
            news_by_date.append({
                'date': date,
                'items': news_items
            })
        
        # Render the template
        html_content = template.render(
            news_by_date=news_by_date,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Write the main index.html
        with open(os.path.join(self.docs_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def get_css_content(self):
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f6f8fa;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2em;
            padding: 1em;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .date-section {
            margin-bottom: 30px;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .date-header {
            background-color: #0366d6;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .news-item {
            border-bottom: 1px solid #eaecef;
            padding: 15px 0;
        }
        
        .news-item:last-child {
            border-bottom: none;
        }
        
        .time {
            color: #586069;
            font-size: 0.9em;
        }
        
        .title {
            margin: 5px 0;
        }
        
        .chinese-title {
            color: #24292e;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        
        .english-title {
            color: #586069;
            font-size: 1em;
        }
        
        .source {
            color: #0366d6;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .last-updated {
            text-align: center;
            color: #586069;
            font-size: 0.9em;
            margin-top: 2em;
        }
        """ 