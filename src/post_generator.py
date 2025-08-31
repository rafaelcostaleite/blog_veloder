import json
import os
from datetime import datetime

class WordPressPostGenerator:
    def __init__(self):
        self.output_dir = "data/output/post"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_search_data(self):
        search_dir = "data/input/search"
        if not os.path.exists(search_dir):
            return []
        
        search_files = [f for f in os.listdir(search_dir) if f.endswith('.json')]
        all_data = []
        
        for file in search_files:
            with open(os.path.join(search_dir, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append(data)
        
        return all_data
    
    def generate_html_post(self, content, title, meta_description="", tags=""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/post_{timestamp}.html"
        
        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{tags}">
</head>
<body>
    <article>
        <header>
            <h1>{title}</h1>
            <time datetime="{datetime.now().isoformat()}">{datetime.now().strftime('%d/%m/%Y')}</time>
        </header>
        <main>
            {content}
        </main>
        <footer>
            <p><small>Post gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</small></p>
        </footer>
    </article>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return filename
    
    def extract_content_from_search(self, search_data):
        content_pieces = []
        sources = []
        
        for data in search_data:
            if 'results' in data and 'organic' in data['results']:
                for result in data['results']['organic']:
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    
                    if title and snippet:
                        content_pieces.append(f"**{title}**\n{snippet}")
                        if link:
                            sources.append(link)
        
        return content_pieces, sources