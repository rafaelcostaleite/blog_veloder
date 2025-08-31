from crewai_tools import SerperDevTool
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class TriathlonSearchTool:
    """Ferramenta especializada para pesquisa de provas de triathlon"""
    
    def __init__(self):
        self.search_tool = SerperDevTool()
    
    def search_triathlon_events(self, query: str = "triathlon events 2025 brasil") -> str:
        """Pesquisa provas de triathlon e estrutura os dados"""
        
        try:
            # Realiza a pesquisa
            results = self.search_tool.run(query)
            
            # Processa e estrutura os resultados
            structured_data = self._process_search_results(results)
            
            return json.dumps(structured_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"Erro na pesquisa: {str(e)}"
    
    def _process_search_results(self, results: str) -> Dict[str, Any]:
        """Processa os resultados da pesquisa em formato estruturado"""
        
        # Estrutura base dos dados
        triathlon_data = {
            "timestamp": datetime.now().isoformat(),
            "events": [],
            "sources": [],
            "summary": {
                "total_events": 0,
                "upcoming_events": 0,
                "locations": []
            }
        }
        
        # Aqui você processaria os resultados reais da pesquisa
        # Para este exemplo, vamos simular alguns dados estruturados
        sample_events = [
            {
                "name": "Ironman Brasil 2024",
                "location": "Florianópolis, SC",
                "date": "2024-05-26",
                "distance": "Full Distance",
                "registration_open": True,
                "website": "https://ironman.com.br",
                "description": "Principal prova de triathlon long distance do Brasil"
            },
            {
                "name": "Triathlon Internacional de Santos",
                "location": "Santos, SP",
                "date": "2024-09-15",
                "distance": "Olympic Distance",
                "registration_open": True,
                "website": "https://triatlonsantos.com.br",
                "description": "Prova tradicional no litoral paulista"
            }
        ]
        
        triathlon_data["events"] = sample_events
        triathlon_data["summary"]["total_events"] = len(sample_events)
        triathlon_data["summary"]["upcoming_events"] = len(sample_events)
        triathlon_data["summary"]["locations"] = [event["location"] for event in sample_events]
        
        return triathlon_data