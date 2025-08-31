from crewai import Agent
from tools.search_tools import TriathlonSearchTool
from utils.file_handler import FileHandler
import json

class TriathlonResearchAgent:
    """Agente responsável pela pesquisa de provas de triathlon"""
    
    def __init__(self, llm):
        self.search_tool = TriathlonSearchTool()
        self.file_handler = FileHandler()
        
        self.agent = Agent(
            role="Especialista em Pesquisa de Triathlon",
            goal="Pesquisar e coletar informações detalhadas sobre provas de triathlon no Brasil",
            backstory="""Você é um especialista em triathlon com amplo conhecimento sobre 
            competições nacionais e internacionais. Sua missão é encontrar as melhores 
            provas de triathlon, coletando informações precisas sobre datas, locais, 
            distâncias e detalhes de inscrição.""",
            tools=[self.search_tool.search_triathlon_events],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def research_triathlon_events(self) -> str:
        """Executa a pesquisa e salva os resultados em JSON"""
        
        # Query de pesquisa otimizada
        search_queries = [
            "triathlon events Brazil 2025 upcoming races",
            "ironman triathlon Brasil calendar",
            "provas triathlon nacionais brasileiras"
        ]
        
        all_results = []
        
        for query in search_queries:
            result = self.search_tool.search_triathlon_events(query)
            if result:
                all_results.append(json.loads(result))
        
        # Consolida os resultados
        consolidated_data = self._consolidate_results(all_results)
        
        # Salva o arquivo JSON
        output_path = "data/triathlon_events.json"
        self.file_handler.save_json(consolidated_data, output_path)
        
        return f"Pesquisa concluída! Dados salvos em {output_path}"
    
    def _consolidate_results(self, results_list: list) -> dict:
        """Consolida múltiplos resultados de pesquisa"""
        
        consolidated = {
            "timestamp": results_list[0]["timestamp"] if results_list else "",
            "events": [],
            "sources": [],
            "summary": {
                "total_events": 0,
                "upcoming_events": 0,
                "locations": set()
            }
        }
        
        # Combina eventos de todas as pesquisas
        for result in results_list:
            consolidated["events"].extend(result.get("events", []))
            consolidated["sources"].extend(result.get("sources", []))
        
        # Remove duplicatas e atualiza sumário
        unique_events = []
        seen_names = set()
        
        for event in consolidated["events"]:
            if event["name"] not in seen_names:
                unique_events.append(event)
                seen_names.add(event["name"])
                consolidated["summary"]["locations"].add(event["location"])
        
        consolidated["events"] = unique_events
        consolidated["summary"]["total_events"] = len(unique_events)
        consolidated["summary"]["upcoming_events"] = len(unique_events)
        consolidated["summary"]["locations"] = list(consolidated["summary"]["locations"])
        
        return consolidated