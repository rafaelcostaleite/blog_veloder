import requests
import json
import os
import tempfile
import re
from datetime import datetime
from crewai_tools import BaseTool
import markdown

class SerperSearchTool(BaseTool):
    name: str = "Serper Search"
    description: str = "Ferramenta para pesquisar informações na internet usando Google Search via API SERPER."
    api_key: str = ""
    base_url: str = "https://google.serper.dev/search"

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
    
    def _run(self, query: str) -> str:
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': 10,
            'gl': 'br',
            'hl': 'pt'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json()
            
            # Retornar dados JSON para o próximo agente (sem salvar em data/)
            return json.dumps(results, ensure_ascii=False, indent=2)
            
        except requests.exceptions.RequestException as e:
            return f"Erro na pesquisa: {e}"

class PostWriterTool(BaseTool):
    name: str = "Post Writer"
    description: str = "Ferramenta para criar posts HTML para WordPress e salvar na pasta output."
    
    def _run(self, content: str) -> str:
        try:
            # Criar diretório se não existir
            output_dir = "data/output/post"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/post_{timestamp}.html"
            
            # Salvar o conteúdo HTML
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Post HTML salvo com sucesso em: {filename}"
            
        except Exception as e:
            return f"Erro ao salvar post: {e}"


class DesignTool(BaseTool):
    name: str = "Design Tool"
    description: str = "Ferramenta para converter markdown em HTML responsivo usando template."
    
    def _run(self, markdown_content: str, title: str = "", meta_description: str = "", keywords: str = "") -> str:
        try:
            # Ler o template
            template_path = "data/input/template/template.html"
            if not os.path.exists(template_path):
                return f"Erro: Template não encontrado em {template_path}"
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Converter markdown para HTML
            html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
            
            # Gerar data atual
            now = datetime.now()
            
            # Substituir placeholders no template
            html_output = template.replace('{{TITLE}}', title)
            html_output = html_output.replace('{{META_DESCRIPTION}}', meta_description)
            html_output = html_output.replace('{{KEYWORDS}}', keywords)
            html_output = html_output.replace('{{CONTENT}}', html_content)
            html_output = html_output.replace('{{DATETIME}}', now.isoformat())
            html_output = html_output.replace('{{DATE}}', now.strftime('%d/%m/%Y'))
            html_output = html_output.replace('{{GENERATION_DATE}}', now.strftime('%d/%m/%Y às %H:%M'))
            html_output = html_output.replace('{{URL}}', '#')  # Placeholder para URL
            
            return html_output
            
        except Exception as e:
            return f"Erro ao processar design: {e}"


class SEOTool(BaseTool):
    name: str = "SEO Tool"
    description: str = "Ferramenta para otimizar HTML com melhores práticas de SEO."
    
    def _run(self, html_content: str) -> str:
        try:
            # Aplicar otimizações de SEO
            optimized_html = html_content
            
            # 1. Adicionar estrutura de dados (JSON-LD)
            json_ld = '''
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{{TITLE}}",
        "description": "{{META_DESCRIPTION}}",
        "author": {
            "@type": "Organization",
            "name": "Blog Veloder"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Blog Veloder"
        },
        "datePublished": "{{DATETIME}}",
        "dateModified": "{{DATETIME}}"
    }
    </script>'''
            
            # Inserir JSON-LD antes do </head>
            optimized_html = optimized_html.replace('</head>', f'{json_ld}\n</head>')
            
            # 2. Otimizar imagens (adicionar alt vazios se não tiver)
            optimized_html = re.sub(r'<img(?![^>]*alt=)', '<img alt=""', optimized_html)
            
            # 3. Adicionar meta robots
            robots_meta = '    <meta name="robots" content="index, follow">\n'
            optimized_html = optimized_html.replace('<meta name="viewport"', f'{robots_meta}    <meta name="viewport"')
            
            # 4. Adicionar canonical URL placeholder
            canonical = '    <link rel="canonical" href="{{CANONICAL_URL}}">\n'
            optimized_html = optimized_html.replace('<meta name="twitter:description"', f'{canonical}    <meta name="twitter:description"')
            
            # 5. Otimizar headings (verificar hierarquia)
            # Garantir que há apenas um H1
            h1_count = len(re.findall(r'<h1[^>]*>', optimized_html))
            if h1_count > 1:
                # Converter H1 extras para H2
                h1_matches = re.finditer(r'<h1([^>]*)>(.*?)</h1>', optimized_html)
                matches_list = list(h1_matches)
                for i, match in enumerate(matches_list[1:], 1):  # Pular o primeiro H1
                    replacement = f'<h2{match.group(1)}>{match.group(2)}</h2>'
                    optimized_html = optimized_html.replace(match.group(0), replacement, 1)
            
            # 6. Adicionar meta de tempo de leitura
            word_count = len(re.findall(r'\w+', optimized_html))
            reading_time = max(1, word_count // 200)  # 200 palavras por minuto
            reading_meta = f'    <meta name="reading-time" content="{reading_time} min">\n'
            optimized_html = optimized_html.replace('<meta name="author"', f'{reading_meta}    <meta name="author"')
            
            # Salvar o HTML otimizado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "data/output/post"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = f"{output_dir}/post_seo_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(optimized_html)
            
            return f"HTML otimizado para SEO salvo em: {filename}"
            
        except Exception as e:
            return f"Erro ao otimizar SEO: {e}"
