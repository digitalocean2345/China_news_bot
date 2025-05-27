import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import pytz
import logging

class PageGenerator:
    def __init__(self, docs_dir='docs'):
        self.docs_dir = docs_dir
        self.template_dir = 'templates'
        
        # Create docs directory if it doesn't exist
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # Create .nojekyll file to disable GitHub Pages Jekyll processing
        with open(os.path.join(self.docs_dir, '.nojekyll'), 'w') as f:
            pass
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def generate_pages(self, data):
        """Generate the HTML pages from the news data"""
        try:
            # Get IST timezone
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
            
            # Organize news by date and then by source
            news_by_date = {}
            headlines = data.get("headlines", {})
            
            # Sort dates in reverse chronological order
            sorted_dates = sorted(headlines.keys(), reverse=True)
            
            for date in sorted_dates:
                # Group items by source for this date
                items_by_source = {}
                for item in reversed(headlines[date]):  # Reverse to keep newest first
                    source = item['source']
                    if source not in items_by_source:
                        items_by_source[source] = []
                    items_by_source[source].append(item)
                
                # Sort sources alphabetically
                sorted_sources = sorted(items_by_source.keys())
                
                # Create the final structure for this date
                news_by_date[date] = {
                    'sources': sorted_sources,
                    'items_by_source': items_by_source
                }
            
            # Get the template
            template = self.env.get_template('index.html')
            
            # Render the template
            html_content = template.render(
                current_time=current_time,
                news_by_date=news_by_date
            )
            
            # Write the rendered HTML to index.html
            index_path = os.path.join(self.docs_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logging.info(f"Successfully generated HTML page with {len(news_by_date)} dates of news")
            
        except Exception as e:
            logging.error(f"Error generating HTML pages: {e}", exc_info=True)
            raise

    def create_initial_page(self):
        """Create a basic index.html file"""
        index_path = os.path.join(self.docs_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>China News Bot</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>China News Bot</h1>
        <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    <div class="content">
        <p>News updates will appear here soon.</p>
    </div>
</body>
</html>
''')

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