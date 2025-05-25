import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil

class PageGenerator:
    def __init__(self, docs_dir='docs'):
        self.docs_dir = docs_dir
        self.template_dir = 'templates'
        
        # Recreate docs directory
        if os.path.exists(self.docs_dir):
            shutil.rmtree(self.docs_dir)
        os.makedirs(self.docs_dir)
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Create .nojekyll file
        with open(os.path.join(self.docs_dir, '.nojekyll'), 'w') as f:
            pass
        
        # Create initial index.html
        self.create_initial_page()
        
        # Copy static assets if they don't exist
        self.create_static_assets()
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
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
    
    def generate_pages(self, data):
        """Generate the HTML pages from the news data"""
        # Load the news data
        try:
            with open('headlines.json', 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        except FileNotFoundError:
            news_data = {"headlines": {}}

        # Get the latest date's news
        dates = sorted(news_data.get("headlines", {}).keys(), reverse=True)
        latest_news = news_data["headlines"][dates[0]] if dates else []

        # Create index.html
        index_path = os.path.join(self.docs_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_html(latest_news))

    def generate_html(self, news_items):
        """Generate HTML content"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f'''
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
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .news-section {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .news-item {{
            border-bottom: 1px solid #eee;
            padding: 15px 0;
        }}
        .news-item:last-child {{
            border-bottom: none;
        }}
        .chinese-title {{
            font-size: 1.1em;
            color: #333;
            margin-bottom: 5px;
        }}
        .english-title {{
            color: #666;
            margin-bottom: 10px;
        }}
        .meta {{
            color: #888;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>China News Bot</h1>
        <p>Last updated: {current_time}</p>
    </div>
    <div class="news-section">
        <h2>Latest News</h2>
        {''.join(f"""
        <div class="news-item">
            <div class="chinese-title">{item['chinese_title']}</div>
            <div class="english-title">{item['english_title']}</div>
            <div class="meta">
                Source: {item['source']} | 
                <a href="{item['url']}" target="_blank">Read More</a>
            </div>
        </div>
        """ for item in news_items) if news_items else "<p>No news updates available.</p>"}
    </div>
</body>
</html>
'''

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