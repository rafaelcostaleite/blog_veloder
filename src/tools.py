import requests
import json
import os
from datetime import datetime
from crewai_tools import BaseTool

class SerperSearchTool(BaseTool):
    name: str = "Serper Search"
    description: str = "Ferramenta para pesquisar informações na internet usando Google Search via API SERPER. Salva automaticamente os resultados em JSON."

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
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
            
            # Salvar automaticamente
            filename = save_search_results(query, results)
            
            # Retornar resumo para o agente
            organic_results = results.get('organic', [])
            summary = f"Encontrados {len(organic_results)} resultados para '{query}':\n\n"
            
            for i, result in enumerate(organic_results[:5], 1):
                summary += f"{i}. {result.get('title', 'N/A')}\n"
                summary += f"   {result.get('snippet', 'N/A')}\n"
                summary += f"   URL: {result.get('link', 'N/A')}\n\n"
            
            summary += f"Dados completos salvos em: {filename}"
            return summary
            
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

def save_search_results(query, results, output_dir="data/input/search"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/search_{timestamp}.json"
    
    search_data = {
        "query": query,
        "timestamp": timestamp,
        "results": results,
        "total_results": len(results.get('organic', [])) if results else 0
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False, indent=2)
    
    return filename