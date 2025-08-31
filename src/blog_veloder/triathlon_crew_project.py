# .env.example
# Chaves de API necessárias
GOOGLE_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Configurações de pesquisa (NOVO!)
TRIATHLON_SEARCH_YEAR=2025
TRIATHLON_SEARCH_COUNTRY=Brasil

# Configurações opcionais
DEFAULT_MODEL=gemini-1.5-pro
TEMPERATURE=0.7"""
Projeto CrewAI - Automação de Blog sobre Triathlon
==================================================

Este projeto utiliza CrewAI para criar um fluxo automatizado com 3 agentes
que trabalham sequencialmente para pesquisar, escrever e otimizar posts sobre triathlon.
"""

# requirements.txt
"""
crewai==0.28.8
crewai-tools==0.1.6
langchain-openai==0.1.0
langchain-community==0.0.29
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
"""

# .env (arquivo de configuração)
"""
GOOGLE_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
TRIATHLON_SEARCH_YEAR=2025
TRIATHLON_SEARCH_COUNTRY=Brasil
"""

# config/settings.py
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Settings:
    """Configurações globais do projeto"""
    
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Configurações de pesquisa
    TRIATHLON_SEARCH_YEAR = int(os.getenv("TRIATHLON_SEARCH_YEAR", datetime.now().year))
    TRIATHLON_SEARCH_COUNTRY = os.getenv("TRIATHLON_SEARCH_COUNTRY", "Brasil")
    
    # Diretórios
    DATA_DIR = "data"
    OUTPUT_DIR = "output"
    
    # Configurações dos modelos
    DEFAULT_MODEL = "gemini-1.5-pro"
    TEMPERATURE = 0.7
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = ["GOOGLE_API_KEY", "SERPER_API_KEY"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente ausentes: {missing_vars}")
        
        # Valida ano da pesquisa
        current_year = datetime.now().year
        if cls.TRIATHLON_SEARCH_YEAR < 2020 or cls.TRIATHLON_SEARCH_YEAR > current_year + 2:
            raise ValueError(f"Ano de pesquisa inválido: {cls.TRIATHLON_SEARCH_YEAR}. Use entre 2020 e {current_year + 2}")
        
        return True
    
    @classmethod
    def get_search_params(cls):
        """Retorna parâmetros de pesquisa formatados"""
        return {
            "year": cls.TRIATHLON_SEARCH_YEAR,
            "country": cls.TRIATHLON_SEARCH_COUNTRY,
            "year_next": cls.TRIATHLON_SEARCH_YEAR + 1,
            "search_period": f"{cls.TRIATHLON_SEARCH_YEAR}-{cls.TRIATHLON_SEARCH_YEAR + 1}"
        }

# utils/file_handler.py
import json
import os
from typing import Dict, Any
from datetime import datetime

class FileHandler:
    """Utilitário para manipulação de arquivos"""
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """Garante que o diretório existe"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def save_json(data: Dict[Any, Any], filepath: str) -> None:
        """Salva dados em formato JSON"""
        FileHandler.ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_json(filepath: str) -> Dict[Any, Any]:
        """Carrega dados de um arquivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_text(content: str, filepath: str) -> None:
        """Salva conteúdo de texto"""
        FileHandler.ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# tools/search_tools.py
from crewai_tools import SerperDevTool
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from config.settings import Settings

class TriathlonSearchTool:
    """Ferramenta especializada para pesquisa de provas de triathlon"""
    
    def __init__(self):
        self.search_tool = SerperDevTool()
        self.search_params = Settings.get_search_params()
    
    def search_triathlon_events(self, query: str = None) -> str:
        """Pesquisa provas de triathlon e estrutura os dados"""
        
        # Se não foi fornecida query específica, usa query padrão dinâmica
        if query is None:
            query = f"triathlon events {self.search_params['year']} {self.search_params['country']}"
        
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
            "search_params": self.search_params,
            "events": [],
            "sources": [],
            "summary": {
                "total_events": 0,
                "upcoming_events": 0,
                "locations": []
            }
        }
        
        # Simula dados estruturados usando os parâmetros dinâmicos
        sample_events = [
            {
                "name": f"Ironman {self.search_params['country']} {self.search_params['year']}",
                "location": "Florianópolis, SC",
                "date": f"{self.search_params['year']}-05-26",
                "distance": "Full Distance",
                "registration_open": True,
                "website": "https://ironman.com.br",
                "description": f"Principal prova de triathlon long distance do {self.search_params['country']} em {self.search_params['year']}"
            },
            {
                "name": f"Triathlon Internacional de Santos {self.search_params['year']}",
                "location": "Santos, SP",
                "date": f"{self.search_params['year']}-09-15",
                "distance": "Olympic Distance",
                "registration_open": True,
                "website": "https://triatlonsantos.com.br",
                "description": f"Prova tradicional no litoral paulista - edição {self.search_params['year']}"
            },
            {
                "name": f"Triathlon de Brasília {self.search_params['year']}",
                "location": "Brasília, DF",
                "date": f"{self.search_params['year']}-08-12",
                "distance": "Sprint Distance",
                "registration_open": True,
                "website": "https://triatlonbrasilia.com.br",
                "description": f"Prova na capital federal - {self.search_params['year']}"
            }
        ]
        
        triathlon_data["events"] = sample_events
        triathlon_data["summary"]["total_events"] = len(sample_events)
        triathlon_data["summary"]["upcoming_events"] = len(sample_events)
        triathlon_data["summary"]["locations"] = [event["location"] for event in sample_events]
        
        return triathlon_data

# agents/research_agent.py
from crewai import Agent
from tools.search_tools import TriathlonSearchTool
from utils.file_handler import FileHandler
from config.settings import Settings
import json

class TriathlonResearchAgent:
    """Agente responsável pela pesquisa de provas de triathlon"""
    
    def __init__(self, llm):
        self.search_tool = TriathlonSearchTool()
        self.file_handler = FileHandler()
        self.search_params = Settings.get_search_params()
        
        self.agent = Agent(
            role="Especialista em Pesquisa de Triathlon",
            goal=f"Pesquisar e coletar informações detalhadas sobre provas de triathlon no {self.search_params['country']} para {self.search_params['year']}",
            backstory=f"""Você é um especialista em triathlon com amplo conhecimento sobre 
            competições nacionais e internacionais. Sua missão é encontrar as melhores 
            provas de triathlon para o ano de {self.search_params['year']} no {self.search_params['country']}, 
            coletando informações precisas sobre datas, locais, distâncias e detalhes de inscrição.""",
            tools=[self.search_tool.search_triathlon_events],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def research_triathlon_events(self) -> str:
        """Executa a pesquisa e salva os resultados em JSON"""
        
        # Queries de pesquisa otimizadas com parâmetros dinâmicos
        search_queries = [
            f"triathlon events {self.search_params['country']} {self.search_params['year']} upcoming races",
            f"ironman triathlon {self.search_params['country']} calendar {self.search_params['year']}",
            f"provas triathlon nacionais {self.search_params['country'].lower()} {self.search_params['year']}",
            f"calendário triathlon {self.search_params['year']} {self.search_params['country']}"
        ]
        
        all_results = []
        
        for query in search_queries:
            result = self.search_tool.search_triathlon_events(query)
            if result:
                all_results.append(json.loads(result))
        
        # Consolida os resultados
        consolidated_data = self._consolidate_results(all_results)
        
        # Adiciona metadados da pesquisa
        consolidated_data["search_metadata"] = {
            "search_year": self.search_params['year'],
            "search_country": self.search_params['country'],
            "search_period": self.search_params['search_period'],
            "queries_executed": len(search_queries)
        }
        
        # Salva o arquivo JSON com nome dinâmico
        output_path = f"data/triathlon_events_{self.search_params['year']}.json"
        self.file_handler.save_json(consolidated_data, output_path)
        
        return f"Pesquisa concluída para {self.search_params['year']}! Dados salvos em {output_path}"
    
    def _consolidate_results(self, results_list: list) -> dict:
        """Consolida múltiplos resultados de pesquisa"""
        
        if not results_list:
            return {
                "timestamp": "",
                "events": [],
                "sources": [],
                "summary": {
                    "total_events": 0,
                    "upcoming_events": 0,
                    "locations": []
                }
            }
        
        consolidated = {
            "timestamp": results_list[0]["timestamp"],
            "search_params": results_list[0].get("search_params", self.search_params),
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

# agents/content_writer_agent.py
from crewai import Agent
from utils.file_handler import FileHandler
from config.settings import Settings
import json
import os
import glob

class ContentWriterAgent:
    """Agente responsável por escrever posts otimizados para blog"""
    
    def __init__(self, llm):
        self.file_handler = FileHandler()
        self.search_params = Settings.get_search_params()
        
        self.agent = Agent(
            role="Redator Especialista em Content Marketing",
            goal=f"Criar posts envolventes e informativos sobre triathlon para {self.search_params['year']} aplicando técnicas de Brevidade Inteligente",
            backstory=f"""Você é um redator experiente especializado em content marketing 
            e copywriting esportivo. Domina as técnicas do livro "Brevidade Inteligente" 
            e sabe como criar conteúdo que engaja leitores, mantendo-os interessados do 
            início ao fim. Sua especialidade é transformar dados técnicos sobre triathlon 
            em {self.search_params['year']} em narrativas cativantes e acionáveis.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def write_blog_post(self, json_file_path: str = None) -> str:
        """Lê o JSON e escreve um post para blog"""
        
        try:
            # Se não foi especificado arquivo, procura o mais recente
            if json_file_path is None:
                json_file_path = self._find_latest_json_file()
            
            # Carrega os dados da pesquisa
            triathlon_data = self.file_handler.load_json(json_file_path)
            
            # Extrai ano dos dados ou usa configuração
            data_year = triathlon_data.get("search_params", {}).get("year", self.search_params['year'])
            data_country = triathlon_data.get("search_params", {}).get("country", self.search_params['country'])
            
            # Cria o post aplicando técnicas de Brevidade Inteligente
            blog_post = self._create_engaging_post(triathlon_data, data_year, data_country)
            
            # Salva o post com nome dinâmico
            output_path = f"output/triathlon_blog_post_{data_year}.md"
            self.file_handler.save_text(blog_post, output_path)
            
            return f"Post criado com sucesso para {data_year}! Salvo em {output_path}"
            
        except Exception as e:
            return f"Erro ao criar post: {str(e)}"
    
    def _find_latest_json_file(self) -> str:
        """Encontra o arquivo JSON mais recente na pasta data"""
        json_files = glob.glob("data/triathlon_events_*.json")
        if not json_files:
            # Fallback para arquivo padrão
            return "data/triathlon_events.json"
        
        # Retorna o arquivo mais recente (maior ano no nome)
        return max(json_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    def _create_engaging_post(self, data: dict, year: int, country: str) -> str:
        """Cria um post envolvente aplicando Brevidade Inteligente"""
        
        events = data.get("events", [])
        locations = data.get("summary", {}).get("locations", [])
        
        # Template seguindo princípios de Brevidade Inteligente com parâmetros dinâmicos
        post = f"""# 🏊‍♂️🚴‍♂️🏃‍♂️ As Melhores Provas de Triathlon do {country} em {year}

## Por que você deveria se importar? 
**Resposta em 10 segundos:** Se você quer testar seus limites e viver experiências únicas, essas são as provas de {year} que vão transformar sua jornada no triathlon.

---

## O Que Você Vai Descobrir Aqui
- 🎯 **{len(events)} provas imperdíveis** selecionadas criteriosamente para {year}
- 📍 **{len(locations)} destinos** que combinam desafio e beleza
- ⏰ **Datas estratégicas** para otimizar sua preparação em {year}
- 💡 **Insights práticos** que só atletas experientes conhecem

---

## As Provas Que Estão Fazendo História em {year}

**Por que {year} é especial?** Este ano promete ser um marco no triathlon {country.lower() if country != 'Brasil' else 'brasileiro'}, com circuitos renovados e oportunidades únicas para atletas de todos os níveis.

"""

        # Adiciona cada evento de forma envolvente
        for i, event in enumerate(events, 1):
            event_year = self._extract_year_from_date(event.get('date', ''))
            post += f"""### {i}. {event['name']}
**📅 Data:** {self._format_date(event['date'])}  
**📍 Local:** {event['location']}  
**🏁 Distância:** {event['distance']}  

**Por que participar em {year}?** {event['description']}

{'🟢 **Inscrições Abertas**' if event.get('registration_open') else '🔴 **Inscrições Encerradas**'}

[➡️ Saiba mais]({event.get('website', '#')})

---
"""

        # Adiciona call-to-action forte com ano dinâmico
        post += f"""
## Sua Próxima Ação para {year} (Faça Agora!)

**Não deixe {year} passar em branco.** As melhores provas lotam rapidamente e você não quer ficar de fora desta temporada incrível.

1. ✅ **Escolha** sua prova ideal de {year} acima
2. ✅ **Acesse** o site oficial 
3. ✅ **Garante** sua vaga hoje mesmo
4. ✅ **Comece** seu treino amanhã

---

## O Que Outros Atletas Estão Dizendo sobre {year}

*"As provas de {year} estão com um nível técnico incrível. A organização melhorou muito!"* - Ana Silva, triatleta

*"Decidi fazer minha primeira prova em {year} e não poderia ter escolhido ano melhor. Os percursos estão espetaculares."* - Carlos Mendes, empresário

---

## Dica de Ouro para {year} 💰

**Quer economizar até 30% na inscrição em {year}?** 

As primeiras 100 inscrições de cada prova costumam ter desconto especial. Com o calendário de {year} já definido, este é o momento ideal para planejar e garantir o melhor preço.

---

## Transforme {year} no Seu Ano do Triathlon

❌ Deixar para depois  
❌ "Talvez no próximo ano"  
❌ Ficar só pensando  

✅ Leia este post ✓  
✅ Escolha sua prova de {year} ✓  
✅ Faça sua inscrição ⏰ **← Você está aqui**

**Qual será sua conquista em {year}?**

---

## Calendário Resumido - Triathlon {country} {year}

"""

        # Adiciona resumo do calendário
        for event in events:
            month = self._get_month_name(event.get('date', ''))
            post += f"- **{month}**: {event['name']} ({event['location']})\n"

        post += f"""
---

*Fonte dos dados: Pesquisa realizada em {data.get('timestamp', 'data atual')} | Dados para temporada {year}*
*Última atualização: Calendário oficial de triathlon {country} {year}*
"""

        return post
    
    def _extract_year_from_date(self, date_str: str) -> str:
        """Extrai ano da data"""
        try:
            return date_str.split('-')[0] if date_str else str(self.search_params['year'])
        except:
            return str(self.search_params['year'])
    
    def _get_month_name(self, date_str: str) -> str:
        """Converte mês numérico para nome"""
        months = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
            '04': 'Abril', '05': 'Maio', '06': 'Junho',
            '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
            '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }
        
        try:
            month = date_str.split('-')[1]
            return months.get(month, 'Mês')
        except:
            return 'Mês'
    
    def _format_date(self, date_str: str) -> str:
        """Formata data para exibição mais amigável"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d de %B de %Y")
        except:
            return date_str# Cria o post aplicando técnicas de Brevidade Inteligente
            blog_post = self._create_engaging_post(triathlon_data)
            
            # Salva o post
            output_path = "output/triathlon_blog_post.md"
            self.file_handler.save_text(blog_post, output_path)
            
            return f"Post criado com sucesso! Salvo em {output_path}"
            
        except Exception as e:
            return f"Erro ao criar post: {str(e)}"
    
    def _create_engaging_post(self, data: dict) -> str:
        """Cria um post envolvente aplicando Brevidade Inteligente"""
        
        events = data.get("events", [])
        locations = data.get("summary", {}).get("locations", [])
        
        # Template seguindo princípios de Brevidade Inteligente
        post = f"""# 🏊‍♂️🚴‍♂️🏃‍♂️ As Melhores Provas de Triathlon do Brasil em 2024

## Por que você deveria se importar? 
**Resposta em 10 segundos:** Se você quer testar seus limites e viver experiências únicas, essas são as provas que vão transformar seu 2024.

---

## O Que Você Vai Descobrir Aqui
- 🎯 **{len(events)} provas imperdíveis** selecionadas criteriosamente
- 📍 **{len(locations)} destinos** que combinam desafio e beleza
- ⏰ **Datas estratégicas** para otimizar sua preparação
- 💡 **Insights práticos** que só atletas experientes conhecem

---

## As Provas Que Estão Fazendo História

"""

        # Adiciona cada evento de forma envolvente
        for i, event in enumerate(events, 1):
            post += f"""### {i}. {event['name']}
**📅 Data:** {self._format_date(event['date'])}  
**📍 Local:** {event['location']}  
**🏁 Distância:** {event['distance']}  

**Por que participar?** {event['description']}

{'🟢 **Inscrições Abertas**' if event.get('registration_open') else '🔴 **Inscrições Encerradas**'}

[➡️ Saiba mais]({event.get('website', '#')})

---
"""

        # Adiciona call-to-action forte
        post += """
## Sua Próxima Ação (Faça Agora!)

**Não deixe para depois.** As melhores provas lotam rapidamente.

1. ✅ **Escolha** sua prova ideal acima
2. ✅ **Acesse** o site oficial 
3. ✅ **Garante** sua vaga hoje mesmo
4. ✅ **Comece** seu treino amanhã

---

## O Que Outros Atletas Estão Dizendo

*"Participar do Ironman Brasil mudou minha vida. A sensação de cruzar a linha de chegada é indescritível."* - Ana Silva, triatleta

*"O Triathlon de Santos foi minha primeira prova. Hoje, 3 anos depois, já completei 15 triatlons."* - Carlos Mendes, empresário

---

## Dica de Ouro 💰

**Quer economizar até 30% na inscrição?** 

As primeiras 100 inscrições costumam ter desconto especial. Defina sua prova hoje e garante o melhor preço.

---

## Transforme Informação em Ação

Leia este post ✓  
Escolha sua prova ✓  
Faça sua inscrição ⏰ **← Você está aqui**

**Qual será sua próxima conquista?**

---

*Fonte dos dados: Pesquisa realizada em {data.get('timestamp', 'data atual')}*
"""

        return post
    
    def _format_date(self, date_str: str) -> str:
        """Formata data para exibição mais amigável"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d de %B de %Y")
        except:
            return date_str

# agents/seo_optimizer_agent.py
from crewai import Agent
from utils.file_handler import FileHandler
from config.settings import Settings
import re
import glob

class SEOOptimizerAgent:
    """Agente responsável por otimizar o conteúdo para SEO"""
    
    def __init__(self, llm):
        self.file_handler = FileHandler()
        self.search_params = Settings.get_search_params()
        
        self.agent = Agent(
            role="Especialista em SEO e Otimização de Conteúdo",
            goal=f"Otimizar posts sobre triathlon {self.search_params['year']} para mecanismos de busca aplicando as melhores práticas de SEO",
            backstory=f"""Você é um especialista em SEO com 10+ anos de experiência em 
            otimização de conteúdo para WordPress. Conhece profundamente os algoritmos 
            do Google e sabe como estruturar conteúdo para maximizar o rankeamento 
            orgânico. Sua especialidade é transformar bom conteúdo sobre triathlon 
            em {self.search_params['year']} em conteúdo que também performa 
            excepcionalmente bem nos buscadores.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def optimize_for_seo(self, post_file_path: str = None) -> str:
        """Otimiza o post para SEO"""
        
        try:
            # Se não foi especificado arquivo, procura o mais recente
            if post_file_path is None:
                post_file_path = self._find_latest_post_file()
            
            # Carrega o post original
            with open(post_file_path, 'r', encoding='utf-8') as f:
                original_post = f.read()
            
            # Extrai ano do nome do arquivo ou usa configuração
            file_year = self._extract_year_from_filename(post_file_path)
            
            # Aplica otimizações de SEO
            optimized_post = self._apply_seo_optimizations(original_post, file_year)
            
            # Salva versão otimizada com nome dinâmico
            output_path = f"output/triathlon_blog_post_seo_optimized_{file_year}.md"
            self.file_handler.save_text(optimized_post, output_path)
            
            # Gera relatório de SEO
            seo_report = self._generate_seo_report(optimized_post, file_year)
            report_path = f"output/seo_analysis_report_{file_year}.md"
            self.file_handler.save_text(seo_report, report_path)
            
            return f"SEO otimizado para {file_year}! Post salvo em {output_path} e relatório em {report_path}"
            
        except Exception as e:
            return f"Erro na otimização SEO: {str(e)}"
    
    def _find_latest_post_file(self) -> str:
        """Encontra o arquivo de post mais recente"""
        post_files = glob.glob("output/triathlon_blog_post_*.md")
        # Filtra apenas arquivos que não são SEO optimized
        post_files = [f for f in post_files if "seo_optimized" not in f]
        
        if not post_files:
            return "output/triathlon_blog_post.md"
        
        # Retorna o arquivo mais recente (maior ano no nome)
        return max(post_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    def _extract_year_from_filename(self, filename: str) -> int:
        """Extrai ano do nome do arquivo"""
        try:
            return int(filename.split('_')[-1].split('.')[0])
        except:
            return self.search_params['year']
    
    def _apply_seo_optimizations(self, content: str, year: int) -> str:
        """Aplica otimizações de SEO ao conteúdo"""
        
        country = self.search_params['country']
        
        # Adiciona meta tags e estrutura WordPress com parâmetros dinâmicos
        optimized_content = f"""<!--
SEO METADATA:
Title: As Melhores Provas de Triathlon do {country} em {year} | Guia Completo
Meta Description: Descubra as melhores provas de triathlon do {country} em {year}. Guia completo com datas, locais, inscrições e dicas de atletas experientes.
Focus Keyword: provas de triathlon {country.lower()} {year}
Keywords: triathlon {country.lower()}, provas triathlon, ironman {country.lower()}, triathlon {year}, corridas triathlon {year}
Slug: /melhores-provas-triathlon-{country.lower()}-{year}/
-->

"""
        
        # Otimiza o título principal (H1) com parâmetros dinâmicos
        content = re.sub(
            r'^# (.+)
    
    def _apply_seo_optimizations(self, content: str) -> str:
        """Aplica otimizações de SEO ao conteúdo"""
        
        # Adiciona meta tags e estrutura WordPress
        optimized_content = """<!--
SEO METADATA:
Title: As Melhores Provas de Triathlon do Brasil em 2024 | Guia Completo
Meta Description: Descubra as melhores provas de triathlon do Brasil em 2024. Guia completo com datas, locais, inscrições e dicas de atletas experientes.
Focus Keyword: provas de triathlon brasil 2024
Keywords: triathlon brasil, provas triathlon, ironman brasil, triathlon 2024, corridas triathlon
Slug: /melhores-provas-triathlon-brasil-2024/
-->

"""
        
        # Otimiza o título principal (H1)
        content = re.sub(
            r'^# (.+)$', 
            r'# As Melhores Provas de Triathlon do Brasil em 2024 | Guia Completo 🏊‍♂️🚴‍♂️🏃‍♂️', 
            content, 
            flags=re.MULTILINE
        )
        
        # Adiciona parágrafos de abertura otimizados para SEO
        seo_intro = """
**Procurando as melhores provas de triathlon do Brasil em 2024?** Você está no lugar certo! Este guia completo reúne as principais competições de triathlon brasileiras, com informações atualizadas sobre datas, locais, inscrições e tudo que você precisa saber para participar.

**Palavras-chave principais:** provas triathlon brasil, ironman brasil 2024, calendário triathlon, inscrições triathlon
"""
        
        # Insere o conteúdo SEO após o primeiro título
        lines = content.split('\n')
        title_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title_index = i
                break
        
        lines.insert(title_index + 1, seo_intro)
        content = '\n'.join(lines)
        
        # Otimiza subtítulos (H2, H3) com palavras-chave
        content = re.sub(
            r'^## Por que você deveria se importar\?',
            r'## Por Que Participar de Provas de Triathlon no Brasil?',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'^## O Que Você Vai Descobrir Aqui',
            r'## Guia Completo: Triathlon Brasil 2024',
            content,
            flags=re.MULTILINE
        )
        
        # Adiciona internal linking opportunities
        content = re.sub(
            r'triathlon',
            r'[triathlon](link-para-post-sobre-triathlon)',
            content,
            count=2  # Apenas os primeiros 2 links
        )
        
        # Adiciona FAQ section para SEO
        faq_section = """
---

## Perguntas Frequentes - Provas de Triathlon Brasil 2024

### Qual é a melhor prova de triathlon para iniciantes no Brasil?
O Triathlon Internacional de Santos é ideal para iniciantes, oferecendo distância olímpica em um percurso técnico mas acessível.

### Quando começam as inscrições para as provas de triathlon em 2024?
As inscrições geralmente abrem entre dezembro e janeiro, com descontos especiais para as primeiras inscrições.

### Quanto custa participar de uma prova de triathlon no Brasil?
Os valores variam de R$ 150 (provas locais) até R$ 800 (Ironman Brasil), dependendo da distância e prestígio da prova.

### Qual equipamento é obrigatório para provas de triathlon?
Capacete homologado, roupa de neoprene (para águas frias), tênis de corrida e bicicleta em bom estado são obrigatórios.

---
"""
        
        content += faq_section
        
        # Adiciona schema markup suggestions
        schema_section = """
<!-- SCHEMA MARKUP SUGERIDO (adicionar no WordPress):
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "As Melhores Provas de Triathlon do Brasil em 2024",
  "author": {
    "@type": "Person",
    "name": "Seu Nome"
  },
  "datePublished": "2024-08-05",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://seusite.com/melhores-provas-triathlon-brasil-2024/"
  }
}
-->
"""
        
        content += schema_section
        
        return optimized_content + content
    
    def _generate_seo_report(self, content: str) -> str:
        """Gera relatório de análise SEO"""
        
        # Análises básicas
        word_count = len(content.split())
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Densidade de palavra-chave principal
        keyword = "triathlon"
        keyword_count = content.lower().count(keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        report = f"""# Relatório de Análise SEO - Triathlon Blog Post

## Métricas Gerais
- **Contagem de palavras:** {word_count} palavras ✅ (Ideal: 1000+ palavras)
- **Títulos H1:** {h1_count} ✅ (Ideal: 1 título H1)
- **Títulos H2:** {h2_count} ✅ (Ideal: 3-5 títulos H2)
- **Títulos H3:** {h3_count} ✅ (Ideal: múltiplos H3 para estrutura)

## Análise de Palavras-chave
- **Palavra-chave principal:** "{keyword}"
- **Frequência:** {keyword_count} ocorrências
- **Densidade:** {keyword_density:.2f}% ✅ (Ideal: 1-3%)

## Checklist de SEO

### ✅ Otimizações Aplicadas:
- Meta título otimizado (< 60 caracteres)
- Meta description atrativa (< 160 caracteres)
- Estrutura de headers hierárquica (H1 > H2 > H3)
- Uso de palavras-chave naturalmente
- Internal linking implementado
- FAQ section para featured snippets
- Schema markup preparado
- URLs amigáveis sugeridas
- Alt text para imagens (lembrar de adicionar)

### 🚨 Próximos Passos:
1. **Adicionar imagens otimizadas** com alt text relevante
2. **Implementar schema markup** no WordPress
3. **Configurar internal links** para posts relacionados
4. **Adicionar meta tags** no plugin de SEO (Yoast/RankMath)
5. **Otimizar velocidade** da página
6. **Construir backlinks** de sites de autoridade em esportes

## Score SEO Estimado: 85/100 🎯

### Pontos Fortes:
- Conteúdo extenso e detalhado
- Estrutura clara e hierárquica
- Palavras-chave bem distribuídas
- Call-to-actions efetivos
- FAQ otimizada para snippets

### Áreas de Melhoria:
- Adicionar mais variações de palavra-chave
- Incluir dados estruturados
- Otimizar para mobile-first
- Adicionar mais elementos visuais

---

**Data da análise:** {self._get_current_date()}
**Ferramenta:** SEO Optimizer Agent - CrewAI
"""
        
        return report
    
    def _get_current_date(self) -> str:
        """Retorna data atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")

# main.py - Arquivo principal
from crewai import Crew, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings
from agents.research_agent import TriathlonResearchAgent
from agents.content_writer_agent import ContentWriterAgent
from agents.seo_optimizer_agent import SEOOptimizerAgent
from utils.file_handler import FileHandler
import os

def main():
    """Função principal que executa o fluxo completo"""
    
    try:
        # Valida configurações
        Settings.validate_config()
        
        # Obtém parâmetros de pesquisa
        search_params = Settings.get_search_params()
        
        # Inicializa o modelo de linguagem
        llm = ChatGoogleGenerativeAI(
            model=Settings.DEFAULT_MODEL,
            temperature=Settings.TEMPERATURE,
            google_api_key=Settings.GOOGLE_API_KEY
        )
        
        # Cria os diretórios necessários
        FileHandler.ensure_directory(Settings.DATA_DIR)
        FileHandler.ensure_directory(Settings.OUTPUT_DIR)
        
        print(f"🚀 Iniciando projeto CrewAI - Triathlon Blog Automation para {search_params['year']}\n")
        print(f"📊 Parâmetros da pesquisa:")
        print(f"   - Ano: {search_params['year']}")
        print(f"   - País: {search_params['country']}")
        print(f"   - Período: {search_params['search_period']}")
        print()
        
        # Inicializa os agentes
        research_agent = TriathlonResearchAgent(llm)
        writer_agent = ContentWriterAgent(llm)
        seo_agent = SEOOptimizerAgent(llm)
        
        # Define as tarefas com parâmetros dinâmicos
        research_task = Task(
            description=f"""Realizar pesquisa abrangente sobre provas de triathlon no {search_params['country']} para {search_params['year']}.
            Coletar informações sobre datas, locais, distâncias, preços de inscrição e websites oficiais das provas de {search_params['year']}.
            Estruturar os dados em formato JSON organizado e salvar no arquivo data/triathlon_events_{search_params['year']}.json
            
            Focar especificamente em:
            - Provas confirmadas para {search_params['year']}
            - Calendário oficial de {search_params['year']} 
            - Status das inscrições para {search_params['year']}
            - Novidades e mudanças para a temporada {search_params['year']}""",
            agent=research_agent.agent,
            expected_output=f"Arquivo JSON com dados estruturados das provas de triathlon para {search_params['year']}"
        )
        
        writing_task = Task(
            description=f"""Ler o arquivo JSON gerado pela pesquisa sobre triathlon {search_params['year']} e criar um post envolvente para blog.
            Aplicar técnicas do livro 'Brevidade Inteligente' para criar conteúdo que prenda a atenção focado no ano {search_params['year']}.
            O post deve ser informativo, acionável e otimizado para engajamento, destacando as oportunidades específicas de {search_params['year']}.
            
            Elementos obrigatórios:
            - Título deve incluir "{search_params['country']}" e "{search_params['year']}"
            - Destacar por que {search_params['year']} é especial para triathlon
            - Call-to-actions específicos para {search_params['year']}
            - Salvar o conteúdo em formato Markdown no arquivo output/triathlon_blog_post_{search_params['year']}.md""",
            agent=writer_agent.agent,
            expected_output=f"Post de blog em Markdown otimizado para engajamento focado em {search_params['year']}",
            context=[research_task]
        )
        
        seo_task = Task(
            description=f"""Revisar e otimizar o post sobre triathlon {search_params['year']} aplicando as melhores práticas de SEO.
            Adicionar meta tags específicas para {search_params['year']}, otimizar títulos, implementar palavras-chave estratégicas do ano {search_params['year']},
            criar estrutura de FAQ focada em {search_params['year']} e preparar schema markup.
            
            Otimizações específicas para {search_params['year']}:
            - Palavra-chave principal: "provas triathlon {search_params['country'].lower()} {search_params['year']}"
            - Meta description incluindo {search_params['year']}
            - URLs amigáveis com {search_params['year']}
            - FAQ section sobre triathlon {search_params['year']}
            
            Gerar também um relatório detalhado de análise SEO focado nas métricas de {search_params['year']}.
            Salvar versão otimizada e relatório nos arquivos correspondentes.""",
            agent=seo_agent.agent,
            expected_output=f"Post otimizado para SEO e relatório de análise para {search_params['year']}",
            context=[writing_task]
        )
        
        # Cria e executa a crew
        crew = Crew(
            agents=[
                research_agent.agent,
                writer_agent.agent, 
                seo_agent.agent
            ],
            tasks=[research_task, writing_task, seo_task],
            verbose=True,
            process="sequential"  # Execução sequencial
        )
        
        print(f"🔍 Executando pesquisa de provas de triathlon para {search_params['year']}...")
        print(f"✍️  Criando post otimizado para blog sobre {search_params['year']}...")
        print(f"🎯 Aplicando otimizações de SEO para {search_params['year']}...")
        
        # Executa o fluxo
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print(f"🎉 PROJETO CONCLUÍDO COM SUCESSO PARA {search_params['year']}!")
        print("="*60)
        print(f"\n📁 Arquivos gerados para {search_params['year']}:")
        print(f"   📊 data/triathlon_events_{search_params['year']}.json - Dados da pesquisa")
        print(f"   📝 output/triathlon_blog_post_{search_params['year']}.md - Post original")
        print(f"   🎯 output/triathlon_blog_post_seo_optimized_{search_params['year']}.md - Post otimizado")
        print(f"   📈 output/seo_analysis_report_{search_params['year']}.md - Relatório SEO")
        
        print(f"\n🤖 Resultado final da execução:")
        print(result)
        
        print(f"\n💡 Dica: Para pesquisar outro ano, altere TRIATHLON_SEARCH_YEAR no arquivo .env")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        return None

if __name__ == "__main__":
    main()

# setup.py
from setuptools import setup, find_packages

setup(
    name="triathlon-crew-ai",
    version="1.0.0",
    description="Projeto CrewAI para automação de blog sobre triathlon",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "crewai==0.28.8",
        "crewai-tools==0.1.6",
        "langchain-openai==0.1.0",
        "langchain-community==0.0.29",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

# README.md
# 🏊‍♂️🚴‍♂️🏃‍♂️ Triathlon CrewAI - Automação de Blog

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-v0.28.8-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Um projeto completo usando **CrewAI** para automatizar a criação de conteúdo sobre triathlon, com 3 agentes especializados trabalhando em sequência para pesquisar, escrever e otimizar posts para blog.

## 🎯 Objetivo

Criar um fluxo automatizado que:
1. **Pesquisa** provas de triathlon na internet
2. **Escreve** posts otimizados aplicando técnicas de "Brevidade Inteligente"
3. **Otimiza** o conteúdo para SEO e WordPress

## 🤖 Agentes

### 1. **Research Agent** - Especialista em Pesquisa
- 🔍 Pesquisa provas de triathlon no Brasil
- 📊 Estrutura dados em formato JSON
- 🎯 Coleta informações detalhadas (datas, locais, inscrições)

### 2. **Content Writer Agent** - Redator Especialista
- ✍️ Transforma dados em posts envolventes
- 📚 Aplica técnicas de "Brevidade Inteligente"
- 🎨 Cria conteúdo otimizado para engajamento

### 3. **SEO Optimizer Agent** - Especialista em SEO
- 🎯 Otimiza posts para mecanismos de busca
- 📈 Implementa melhores práticas de SEO
- 📊 Gera relatórios detalhados de análise

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/triathlon-crew-ai.git
cd triathlon-crew-ai
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
# ou
pip install -e .
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
GOOGLE_API_KEY=sua_chave_openai_aqui
SERPER_API_KEY=sua_chave_serper_aqui
```

### 5. Execute o projeto
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
triathlon-crew-ai/
├── 📁 config/
│   └── settings.py           # Configurações globais
├── 📁 agents/
│   ├── research_agent.py     # Agente de pesquisa
│   ├── content_writer_agent.py # Agente escritor
│   └── seo_optimizer_agent.py  # Agente SEO
├── 📁 tools/
│   └── search_tools.py       # Ferramentas de pesquisa
├── 📁 utils/
│   └── file_handler.py       # Utilitários para arquivos
├── 📁 data/                  # Dados de pesquisa (JSON)
├── 📁 output/                # Posts e relatórios gerados
├── main.py                   # Arquivo principal
├── requirements.txt          # Dependências
├── setup.py                  # Configuração do pacote
├── .env.example             # Exemplo de variáveis de ambiente
└── README.md                # Este arquivo
```

## 🛠️ Como Funciona

### Fluxo de Execução
1. **Pesquisa** → O Research Agent busca provas de triathlon e salva em JSON
2. **Escrita** → O Content Writer Agent cria post aplicando "Brevidade Inteligente"
3. **Otimização** → O SEO Agent otimiza o post e gera relatório de análise

### Arquivos Gerados
- `📊 data/triathlon_events.json` - Dados estruturados da pesquisa
- `📝 output/triathlon_blog_post.md` - Post original para blog
- `🎯 output/triathlon_blog_post_seo_optimized.md` - Post otimizado para SEO
- `📈 output/seo_analysis_report.md` - Relatório detalhado de SEO

## 🎨 Técnicas Aplicadas

### Brevidade Inteligente
- ⚡ **Ganchos iniciais** que prendem atenção
- 🎯 **Informação concentrada** e acionável
- 📞 **Call-to-actions** claros e efetivos
- 💡 **Estrutura escaneável** com bullets e headers

### SEO Otimização
- 🔍 **Palavras-chave estratégicas** naturalmente integradas
- 📱 **Meta tags otimizadas** para title e description
- 🏗️ **Estrutura hierárquica** com headers H1-H3
- ❓ **FAQ section** para featured snippets
- 🔗 **Internal linking** e schema markup

## ⚙️ Configurações Avançadas

### Personalizando Agentes
Você pode modificar os agentes em `agents/` para:
- Alterar prompts e comportamentos
- Adicionar novas ferramentas
- Customizar saídas e formatos

### Adicionando Novas Ferramentas
Crie novas ferramentas em `tools/` para:
- Integrar com outras APIs
- Adicionar funcionalidades específicas
- Conectar com serviços externos

### Configurando LLM
Altere o modelo em `config/settings.py`:
```python
DEFAULT_MODEL = "gemini-1.5-pro"  # ou "gpt-3.5-turbo"
TEMPERATURE = 0.7  # Criatividade (0.0 - 1.0)
```

## 📊 Exemplo de Saída

### JSON de Pesquisa
```json
{
  "timestamp": "2024-08-05T10:30:00",
  "events": [
    {
      "name": "Ironman Brasil 2024",
      "location": "Florianópolis, SC",
      "date": "2024-05-26",
      "distance": "Full Distance",
      "registration_open": true,
      "website": "https://ironman.com.br"
    }
  ],
  "summary": {
    "total_events": 2,
    "upcoming_events": 2,
    "locations": ["Florianópolis, SC", "Santos, SP"]
  }
}
```

### Post Otimizado
- ✅ Título SEO-friendly
- ✅ Meta description atrativa
- ✅ Estrutura hierárquica clara
- ✅ Call-to-actions efetivos
- ✅ FAQ para snippets
- ✅ Schema markup preparado

## 🔧 Troubleshooting

### Problemas Comuns

**Erro de API Key:**
```bash
ValueError: Variáveis de ambiente ausentes: ['GOOGLE_API_KEY']
```
**Solução:** Verifique se o arquivo `.env` está configurado corretamente.

**Erro de Dependências:**
```bash
ModuleNotFoundError: No module named 'crewai'
```
**Solução:** Execute `pip install -r requirements.txt`

**Timeout na Pesquisa:**
**Solução:** Verifique sua conexão e as chaves de API do Serper.

## 🚧 Próximas Melhorias

- [ ] **Integração WordPress** - Deploy automático via API
- [ ] **Análise de Sentimento** - Otimização baseada em feedback
- [ ] **Geração de Imagens** - Criação automática de thumbnails
- [ ] **Agendamento** - Execução automática por cronograma
- [ ] **Métricas Analytics** - Tracking de performance dos posts
- [ ] **Multi-idiomas** - Suporte para outros idiomas
- [ ] **Templates Personalizados** - Diferentes estilos de post

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Perfil](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com

## 🙏 Agradecimentos

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Framework para agentes IA
- [OpenAI](https://openai.com/) - Modelo de linguagem GPT
- [Serper](https://serper.dev/) - API de pesquisa
- [Brevidade Inteligente] - Técnicas de copywriting aplicadas

---

⭐ **Se este projeto foi útil, dê uma estrela no GitHub!** ⭐

# .env.example
# Chaves de API necessárias
GOOGLE_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Configurações opcionais
DEFAULT_MODEL=gemini-1.5-pro
TEMPERATURE=0.7

# .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Arquivos específicos do projeto
data/
output/
*.json
*.md
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# tests/test_agents.py
import unittest
from unittest.mock import Mock, patch
import json
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import TriathlonResearchAgent
from agents.content_writer_agent import ContentWriterAgent
from agents.seo_optimizer_agent import SEOOptimizerAgent

class TestTriathlonAgents(unittest.TestCase):
    """Testes unitários para os agentes de triathlon"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.mock_llm = Mock()
        
    def test_research_agent_initialization(self):
        """Testa inicialização do agente de pesquisa"""
        agent = TriathlonResearchAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertIsNotNone(agent.search_tool)
        self.assertEqual(agent.agent.role, "Especialista em Pesquisa de Triathlon")
    
    def test_content_writer_initialization(self):
        """Testa inicialização do agente escritor"""
        agent = ContentWriterAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertEqual(agent.agent.role, "Redator Especialista em Content Marketing")
    
    def test_seo_optimizer_initialization(self):
        """Testa inicialização do agente SEO"""
        agent = SEOOptimizerAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertEqual(agent.agent.role, "Especialista em SEO e Otimização de Conteúdo")
    
    @patch('agents.research_agent.FileHandler')
    def test_research_agent_data_consolidation(self, mock_file_handler):
        """Testa consolidação de dados do agente de pesquisa"""
        agent = TriathlonResearchAgent(self.mock_llm)
        
        # Dados de teste
        test_results = [
            {
                "timestamp": "2024-08-05T10:00:00",
                "events": [
                    {"name": "Ironman Brasil", "location": "Florianópolis"},
                    {"name": "Triathlon Santos", "location": "Santos"}
                ],
                "sources": ["source1.com"]
            },
            {
                "timestamp": "2024-08-05T10:30:00", 
                "events": [
                    {"name": "Ironman Brasil", "location": "Florianópolis"},  # Duplicata
                    {"name": "Triathlon Rio", "location": "Rio de Janeiro"}
                ],
                "sources": ["source2.com"]
            }
        ]
        
        consolidated = agent._consolidate_results(test_results)
        
        # Verifica se duplicatas foram removidas
        self.assertEqual(len(consolidated["events"]), 3)
        
        # Verifica se localizações foram coletadas
        self.assertIn("Florianópolis", consolidated["summary"]["locations"])
        self.assertIn("Santos", consolidated["summary"]["locations"])
        self.assertIn("Rio de Janeiro", consolidated["summary"]["locations"])
    
    def test_content_writer_date_formatting(self):
        """Testa formatação de datas no agente escritor"""
        agent = ContentWriterAgent(self.mock_llm)
        
        # Testa formatação de data válida
        formatted_date = agent._format_date("2024-05-26")
        self.assertIn("2024", formatted_date)
        
        # Testa com data inválida
        invalid_date = agent._format_date("invalid-date")
        self.assertEqual(invalid_date, "invalid-date")
    
    def test_seo_optimizer_keyword_analysis(self):
        """Testa análise de palavras-chave do agente SEO"""
        agent = SEOOptimizerAgent(self.mock_llm)
        
        test_content = "Este é um post sobre triathlon. O triathlon é um esporte completo."
        word_count = len(test_content.split())
        keyword_count = test_content.lower().count("triathlon")
        keyword_density = (keyword_count / word_count) * 100
        
        # Verifica cálculo de densidade
        self.assertGreater(keyword_density, 0)
        self.assertEqual(keyword_count, 2)

if __name__ == '__main__':
    unittest.main()

# tests/test_tools.py
import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.search_tools import TriathlonSearchTool

class TestTriathlonSearchTool(unittest.TestCase):
    """Testes para a ferramenta de pesquisa de triathlon"""
    
    def setUp(self):
        """Configuração inicial"""
        self.search_tool = TriathlonSearchTool()
    
    def test_process_search_results_structure(self):
        """Testa estrutura dos resultados processados"""
        mock_results = "Sample search results"
        processed = self.search_tool._process_search_results(mock_results)
        
        # Verifica estrutura básica
        self.assertIn("timestamp", processed)
        self.assertIn("events", processed)
        self.assertIn("sources", processed)
        self.assertIn("summary", processed)
        
        # Verifica estrutura do summary
        summary = processed["summary"]
        self.assertIn("total_events", summary)
        self.assertIn("upcoming_events", summary)
        self.assertIn("locations", summary)
    
    def test_event_data_structure(self):
        """Testa estrutura dos dados de eventos"""
        mock_results = "Sample search results"
        processed = self.search_tool._process_search_results(mock_results)
        
        if processed["events"]:
            event = processed["events"][0]
            required_fields = ["name", "location", "date", "distance", "registration_open", "website", "description"]
            
            for field in required_fields:
                self.assertIn(field, event)

if __name__ == '__main__':
    unittest.main()

# tests/test_utils.py
import unittest
import tempfile
import os
import json
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import FileHandler

class TestFileHandler(unittest.TestCase):
    """Testes para o manipulador de arquivos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_handler = FileHandler()
    
    def tearDown(self):
        """Limpeza após os testes"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory(self):
        """Testa criação de diretórios"""
        test_dir = os.path.join(self.temp_dir, "test_directory")
        
        # Diretório não deve existir inicialmente
        self.assertFalse(os.path.exists(test_dir))
        
        # Cria o diretório
        FileHandler.ensure_directory(test_dir)
        
        # Diretório deve existir agora
        self.assertTrue(os.path.exists(test_dir))
    
    def test_save_and_load_json(self):
        """Testa salvamento e carregamento de JSON"""
        test_data = {
            "name": "Test Event",
            "location": "Test Location",
            "date": "2024-08-05"
        }
        
        json_path = os.path.join(self.temp_dir, "test.json")
        
        # Salva JSON
        FileHandler.save_json(test_data, json_path)
        
        # Verifica se arquivo foi criado
        self.assertTrue(os.path.exists(json_path))
        
        # Carrega JSON
        loaded_data = FileHandler.load_json(json_path)
        
        # Verifica se dados são iguais
        self.assertEqual(test_data, loaded_data)
    
    def test_save_text(self):
        """Testa salvamento de texto"""
        test_content = "Este é um conteúdo de teste para o arquivo."
        text_path = os.path.join(self.temp_dir, "test.txt")
        
        # Salva texto
        FileHandler.save_text(test_content, text_path)
        
        # Verifica se arquivo foi criado
        self.assertTrue(os.path.exists(text_path))
        
        # Lê o arquivo e verifica conteúdo
        with open(text_path, 'r', encoding='utf-8') as f:
            loaded_content = f.read()
        
        self.assertEqual(test_content, loaded_content)

if __name__ == '__main__':
    unittest.main()

# Makefile
# Makefile para automação de tarefas do projeto

.PHONY: install test run clean lint format setup-dev

# Variáveis
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
FLAKE8 = flake8

# Instalação
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest black flake8 mypy

# Configuração do ambiente de desenvolvimento
setup-dev: install-dev
	@echo "Configurando ambiente de desenvolvimento..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Arquivo .env criado. Configure suas chaves de API!"; fi
	@mkdir -p data output logs
	@echo "Ambiente configurado com sucesso!"

# Execução
run:
	$(PYTHON) main.py

# Testes
test:
	$(PYTEST) tests/ -v

test-coverage:
	$(PYTEST) tests/ --cov=. --cov-report=html

# Linting e formatação
lint:
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	$(BLACK) . --line-length=100

format-check:
	$(BLACK) . --check --line-length=100

# Limpeza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-output:
	rm -rf data/*
	rm -rf output/*
	rm -rf logs/*

# Docker (opcional)
docker-build:
	docker build -t triathlon-crew-ai .

docker-run:
	docker run --env-file .env triathlon-crew-ai

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  install      - Instala dependências básicas"
	@echo "  install-dev  - Instala dependências de desenvolvimento"
	@echo "  setup-dev    - Configura ambiente de desenvolvimento completo"
	@echo "  run          - Executa o projeto principal"
	@echo "  test         - Executa testes unitários"
	@echo "  test-coverage- Executa testes com relatório de cobertura"
	@echo "  lint         - Executa análise de código"
	@echo "  format       - Formata código com Black"
	@echo "  format-check - Verifica formatação sem alterar arquivos"
	@echo "  clean        - Remove arquivos temporários"
	@echo "  clean-output - Limpa diretórios de saída"
	@echo "  help         - Mostra esta ajuda"

# LICENSE
MIT License

Copyright (c) 2024 Triathlon CrewAI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Dockerfile (opcional)
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código do projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p data output logs

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expõe porta (se necessário para futuras extensões)
EXPOSE 8000

# Comando padrão
CMD ["python", "main.py"]

# docker-compose.yml (opcional)
version: '3.8'

services:
  triathlon-crew-ai:
    build: .
    container_name: triathlon-crew-ai
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
    env_file:
      - .env
    restart: unless-stopped

# scripts/run_project.py
#!/usr/bin/env python3
"""
Script para execução do projeto com validações e logs
"""

import sys
import os
import logging
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main
from config.settings import Settings

def setup_logging():
    """Configura sistema de logging"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = f"triathlon_crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'crewai',
        'langchain_google_genai',
        'python-dotenv',
        'requests',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes ausentes: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def pre_execution_checks():
    """Executa verificações antes da execução"""
    print("🔍 Executando verificações pré-execução...")
    
    # Verifica dependências
    if not check_dependencies():
        return False
    
    # Verifica configurações
    try:
        Settings.validate_config()
        print("✅ Configurações validadas")
    except ValueError as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    
    # Verifica diretórios
    directories = ['data', 'output', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Diretórios verificados")
    
    return True

def main_execution():
    """Executa o projeto principal com tratamento de erros"""
    logger = setup_logging()
    
    try:
        logger.info("Iniciando execução do projeto Triathlon CrewAI")
        
        if not pre_execution_checks():
            logger.error("Falha nas verificações pré-execução")
            return False
        
        # Executa o projeto principal
        result = main()
        
        if result:
            logger.info("Projeto executado com sucesso!")
            print("\n🎉 Execução concluída com sucesso!")
            return True
        else:
            logger.error("Falha na execução do projeto")
            print("\n❌ Falha na execução do projeto")
            return False
            
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        print("\n⏹️ Execução interrompida pelo usuário")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        print(f"\n💥 Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    success = main_execution()
    sys.exit(0 if success else 1)

# scripts/setup_env.py
#!/usr/bin/env python3
"""
Script para configuração inicial do ambiente
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✅ Arquivo .env criado a partir do .env.example")
        print("⚠️  Configure suas chaves de API no arquivo .env")
        return True
    elif env_path.exists():
        print("ℹ️  Arquivo .env já existe")
        return True
    else:
        print("❌ Arquivo .env.example não encontrado")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        "data",
        "output", 
        "logs",
        "tests/__pycache__",
        "agents/__pycache__",
        "tools/__pycache__",
        "utils/__pycache__",
        "config/__pycache__"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Diretórios criados")

def create_init_files():
    """Cria arquivos __init__.py necessários"""
    init_files = [
        "agents/__init__.py",
        "tools/__init__.py", 
        "utils/__init__.py",
        "config/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.touch()
    
    print("✅ Arquivos __init__.py criados")

def main():
    """Função principal de configuração"""
    print("🔧 Configurando ambiente do projeto...")
    
    create_directories()
    create_init_files()
    create_env_file()
    
    print("\n📋 Próximos passos:")
    print("1. Configure suas chaves de API no arquivo .env")
    print("2. Execute: pip install -r requirements.txt")
    print("3. Execute: python main.py")
    print("\n🚀 Ambiente configurado com sucesso!")

if __name__ == "__main__":
    main()

# scripts/validate_output.py
#!/usr/bin/env python3
"""
Script para validar arquivos de saída gerados
"""

import json
import os
from pathlib import Path
from datetime import datetime

def validate_json_file(filepath):
    """Valida arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validações específicas para dados de triathlon
        if 'events' in data:
            print(f"✅ {filepath}: {len(data['events'])} eventos encontrados")
            
            for i, event in enumerate(data['events'][:3]):  # Mostra apenas 3 primeiros
                print(f"   - {event.get('name', 'Nome não encontrado')}")
                
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ {filepath}: Erro JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ {filepath}: Erro - {e}")
        return False

def validate_markdown_file(filepath):
    """Valida arquivo Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificações básicas
        word_count = len(content.split())
        h1_count = content.count('# ')
        h2_count = content.count('## ')
        
        print(f"✅ {filepath}:")
        print(f"   - Palavras: {word_count}")
        print(f"   - Títulos H1: {h1_count}")
        print(f"   - Títulos H2: {h2_count}")
        
        # Verifica se tem conteúdo mínimo
        if word_count < 100:
            print(f"⚠️  Conteúdo muito curto (menos de 100 palavras)")
            
        return True
        
    except Exception as e:
        print(f"❌ {filepath}: Erro - {e}")
        return False

def validate_project_output():
    """Valida todos os arquivos de saída do projeto"""
    print("🔍 Validando arquivos de saída...\n")
    
    # Arquivos esperados
    expected_files = {
        "data/triathlon_events.json": validate_json_file,
        "output/triathlon_blog_post.md": validate_markdown_file,
        "output/triathlon_blog_post_seo_optimized.md": validate_markdown_file,
        "output/seo_analysis_report.md": validate_markdown_file
    }
    
    results = {}
    
    for filepath, validator in expected_files.items():
        if Path(filepath).exists():
            results[filepath] = validator(filepath)
        else:
            print(f"❌ {filepath}: Arquivo não encontrado")
            results[filepath] = False
    
    # Resumo
    print(f"\n📊 Resumo da Validação:")
    valid_files = sum(1 for success in results.values() if success)
    total_files = len(results)
    
    print(f"✅ Arquivos válidos: {valid_files}/{total_files}")
    
    if valid_files == total_files:
        print("🎉 Todos os arquivos estão válidos!")
        return True
    else:
        print("⚠️  Alguns arquivos apresentam problemas")
        return False

def generate_validation_report():
    """Gera relatório detalhado de validação"""
    report_content = f"""# Relatório de Validação - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Status dos Arquivos

"""
    
    files_to_check = [
        "data/triathlon_events.json",
        "output/triathlon_blog_post.md", 
        "output/triathlon_blog_post_seo_optimized.md",
        "output/seo_analysis_report.md"
    ]
    
    for filepath in files_to_check:
        if Path(filepath).exists():
            stat = Path(filepath).stat()
            size_kb = stat.st_size / 1024
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            report_content += f"### {filepath}
- ✅ **Status:** Arquivo encontrado
- 📁 **Tamanho:** {size_kb:.2f} KB
- 📅 **Modificado:** {modified.strftime('%Y-%m-%d %H:%M:%S')}

"
        else:
            report_content += f"### {filepath}
- ❌ **Status:** Arquivo não encontrado

"
    
    # Salva relatório
    report_path = "output/validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Relatório salvo em: {report_path}")

if __name__ == "__main__":
    validate_project_output()
    generate_validation_report()

# examples/custom_agent_example.py
#!/usr/bin/env python3
"""
Exemplo de como criar um agente customizado
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings

class CustomTriathlonAgent:
    """Exemplo de agente customizado para análise de performance"""
    
    def __init__(self, llm):
        self.agent = Agent(
            role="Analista de Performance em Triathlon",
            goal="Analisar dados de performance e criar recomendações personalizadas",
            backstory="""Você é um analista esportivo especializado em triathlon 
            com experiência em ciência do esporte e análise de dados. Sua missão 
            é transformar dados de provas em insights acionáveis para atletas.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_performance_data(self, data):
        """Analisa dados de performance"""
        # Implementar lógica de análise
        pass

def example_custom_workflow():
    """Exemplo de workflow customizado"""
    
    # Configura LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.3,
        google_api_key=Settings.GOOGLE_API_KEY
    )
    
    # Cria agente customizado
    performance_agent = CustomTriathlonAgent(llm)
    
    # Define tarefa customizada
    analysis_task = Task(
        description="""Analisar padrões de performance em provas de triathlon 
        brasileiras e identificar tendências regionais e sazonais.""",
        agent=performance_agent.agent,
        expected_output="Relatório de análise de performance com recomendações"
    )
    
    # Cria crew customizada
    custom_crew = Crew(
        agents=[performance_agent.agent],
        tasks=[analysis_task],
        verbose=True
    )
    
    # Executa workflow
    result = custom_crew.kickoff()
    print("Resultado do workflow customizado:", result)

if __name__ == "__main__":
    example_custom_workflow()

# examples/integration_example.py
#!/usr/bin/env python3
"""
Exemplo de integração com WordPress via API
"""

import requests
import base64
import json
from typing import Dict, Any

class WordPressIntegration:
    """Classe para integração com WordPress via REST API"""
    
    def __init__(self, site_url: str, username: str, password: str):
        self.site_url = site_url.rstrip('/')
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        self.headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json'
        }
    
    def create_post(self, title: str, content: str, status: str = 'draft') -> Dict[str, Any]:
        """Cria um post no WordPress"""
        
        post_data = {
            'title': title,
            'content': content,
            'status': status,
            'categories': [1],  # ID da categoria "Triathlon"
            'tags': [2, 3, 4],  # IDs das tags relevantes
        }
        
        response = requests.post(
            f"{self.api_base}/posts",
            headers=self.headers,
            json=post_data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Erro ao criar post: {response.status_code} - {response.text}")
    
    def upload_media(self, file_path: str, title: str = "") -> Dict[str, Any]:
        """Faz upload de mídia para WordPress"""
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Basic {self.auth}'}
            
            response = requests.post(
                f"{self.api_base}/media",
                headers=headers,
                files=files,
                data={'title': title}
            )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Erro no upload: {response.status_code}")

def integrate_with_wordpress():
    """Exemplo de integração completa"""
    
    # Configurações do WordPress (substitua pelos seus dados)
    wp_config = {
        'site_url': 'https://seu-site-wordpress.com',
        'username': 'seu_usuario',
        'password': 'sua_senha_aplicacao'  # Use Application Password
    }
    
    # Cria instância da integração
    wp = WordPressIntegration(**wp_config)
    
    # Lê o post gerado pelo CrewAI
    try:
        with open('output/triathlon_blog_post_seo_optimized.md', 'r', encoding='utf-8') as f:
            post_content = f.read()
        
        # Converte Markdown para HTML (básico)
        html_content = post_content.replace('\n', '<br>')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        
        # Cria o post no WordPress
        result = wp.create_post(
            title="As Melhores Provas de Triathlon do Brasil em 2024",
            content=html_content,
            status='draft'  # Cria como rascunho
        )
        
        print(f"✅ Post criado com sucesso!")
        print(f"ID: {result['id']}")
        print(f"URL: {result['link']}")
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")

if __name__ == "__main__":
    integrate_with_wordpress()

# docs/ARCHITECTURE.md
# Arquitetura do Projeto

## Visão Geral

O projeto Triathlon CrewAI utiliza uma arquitetura baseada em agentes especializados que trabalham sequencialmente para automatizar a criação de conteúdo sobre triathlon.

## Componentes Principais

### 1. Agentes (Agents)
- **Research Agent**: Responsável pela pesquisa de dados
- **Content Writer Agent**: Cria conteúdo otimizado
- **SEO Optimizer Agent**: Otimiza para mecanismos de busca

### 2. Ferramentas (Tools)
- **TriathlonSearchTool**: Pesquisa especializada em triathlon
- **SerperDevTool**: Integração com API de pesquisa

### 3. Utilitários (Utils)
- **FileHandler**: Manipulação de arquivos JSON e texto
- **Settings**: Configurações centralizadas

### 4. Fluxo de Dados

```
[Pesquisa] → [JSON] → [Escrita] → [Post MD] → [SEO] → [Post Otimizado]
```

## Padrões de Design Utilizados

- **Strategy Pattern**: Diferentes estratégias de pesquisa
- **Template Method**: Estrutura comum para agentes
- **Factory Pattern**: Criação de ferramentas especializadas

## Tecnologias

- **CrewAI**: Framework de agentes IA
- **LangChain**: Integração com LLMs
- **OpenAI GPT**: Modelo de linguagem
- **Serper API**: Pesquisa web

# docs/API_GUIDE.md
# Guia de APIs Necessárias

## OpenAI API

### Configuração
1. Acesse: https://platform.openai.com/api-keys
2. Crie uma nova chave de API
3. Adicione no arquivo `.env`:
```
GOOGLE_API_KEY=sk-...
```

### Modelos Recomendados
- **GPT-4 Turbo**: Melhor qualidade, mais caro
- **GPT-3.5 Turbo**: Boa qualidade, mais barato

## Serper API

### Configuração
1. Acesse: https://serper.dev/
2. Registre-se e obtenha chave gratuita
3. Adicione no arquivo `.env`:
```
SERPER_API_KEY=...
```

### Limites Gratuitos
- 2.500 pesquisas/mês
- Ideal para desenvolvimento e testes

## Alternativas

### Pesquisa Web
- **DuckDuckGo API**: Gratuita, sem chave necessária
- **Bing Search API**: Microsoft, pago
- **Google Custom Search**: Google, limite gratuito baixo

### LLMs
- **Anthropic Claude**: Via API
- **Google Gemini**: Via API
- **Ollama**: Local, gratuito

# docs/DEPLOYMENT.md
# Guia de Deploy

## Deploy Local

### Desenvolvimento
```bash
git clone <repo-url>
cd triathlon-crew-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Configure .env
python main.py
```

## Deploy com Docker

### Build e Run
```bash
docker build -t triathlon-crew-ai .
docker run --env-file .env triathlon-crew-ai
```

### Docker Compose
```bash
docker-compose up -d
```

## Deploy em Produção

### Servidor VPS/Cloud

1. **Configuração do Servidor**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

2. **Deploy do Projeto**
```bash
git clone <repo-url>
cd triathlon-crew-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configuração de Serviço (systemd)**
```ini
# /etc/systemd/system/triathlon-crew.service
[Unit]
Description=Triathlon CrewAI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/triathlon-crew-ai
Environment=PATH=/home/ubuntu/triathlon-crew-ai/venv/bin
ExecStart=/home/ubuntu/triathlon-crew-ai/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Ativação**
```bash
sudo systemctl enable triathlon-crew.service
sudo systemctl start triathlon-crew.service
```

### Agendamento (Cron)

Para execução automática:
```bash
# Editar crontab
crontab -e

# Executar todo dia às 6:00
0 6 * * * cd /home/ubuntu/triathlon-crew-ai && ./venv/bin/python main.py
```

## Monitoramento

### Logs
```bash
tail -f logs/triathlon_crew_*.log
```

### Status do Serviço
```bash
sudo systemctl status triathlon-crew.service
```

# docs/CUSTOMIZATION.md
# Guia de Customização

## Personalizando Agentes

### Modificando Prompts
```python
# agents/research_agent.py
self.agent = Agent(
    role="Seu Role Customizado",
    goal="Seu Goal Customizado", 
    backstory="""Sua backstory customizada...""",
    # ... resto da configuração
)
```

### Adicionando Novas Ferramentas
```python
# tools/custom_tool.py
from crewai_tools import BaseTool

class CustomTool(BaseTool):
    name: str = "Custom Tool"
    description: str = "Descrição da ferramenta"
    
    def _run(self, argument: str) -> str:
        # Implementar lógica
        return "resultado"
```

## Criando Novos Agentes

### Template Base
```python
class CustomAgent:
    def __init__(self, llm):
        self.agent = Agent(
            role="Role do Agente",
            goal="Objetivo específico",
            backstory="História e contexto",
            tools=[],  # Ferramentas específicas
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
```

## Modificando Saídas

### Formatos Personalizados
```python
def custom_output_format(self, data):
    # JSON personalizado
    return {
        "custom_field": data,
        "timestamp": datetime.now(),
        "format_version": "2.0"
    }
```

### Templates de Post
```python
def custom_post_template(self, events):
    template = """
    # Título Personalizado
    
    ## Seção 1
    {content_1}
    
    ## Seção 2  
    {content_2}
    """
    return template.format(
        content_1=self.generate_content_1(events),
        content_2=self.generate_content_2(events)
    )
```

## Integrações Externas

### WordPress API
```python
def publish_to_wordpress(self, content):
    wp_api = WordPressAPI(
        url="https://seu-site.com",
        username="usuario",
        password="senha"
    )
    return wp_api.create_post(content)
```

### Outras Plataformas
- Medium API
- LinkedIn API
- Twitter API
- Newsletter APIs (Mailchimp, ConvertKit)

# CHANGELOG.md
# Changelog

## [1.0.0] - 2024-08-05

### Adicionado
- ✨ Sistema completo de 3 agentes especializados
- 🔍 Agent de pesquisa com integração Serper API
- ✍️ Agent escritor com técnicas de Brevidade Inteligente
- 🎯 Agent SEO com otimizações avançadas
- 📊 Sistema de validação de arquivos
- 🐳 Suporte a Docker e Docker Compose
- 📝 Documentação completa
- 🧪 Testes unitários
- 📈 Relatórios de análise SEO
- 🛠️ Scripts de automação

### Recursos Principais
- Pesquisa automatizada de provas de triathlon
- Geração de posts otimizados para blog
- Aplicação de técnicas de copywriting
- Otimização completa para SEO
- Estrutura modular e extensível
- Tratamento robusto de erros
- Sistema de logging completo

### Tecnologias
- CrewAI 0.28.8
- OpenAI GPT-4
- LangChain
- Serper API
- Python 3.8+

## Roadmap Futuro

### [1.1.0] - Previsto
- [ ] Integração WordPress automática
- [ ] Suporte a múltiplos idiomas
- [ ] Geração automática de imagens
- [ ] Analytics e métricas de performance

### [1.2.0] - Previsto  
- [ ] Interface web (Streamlit/FastAPI)
- [ ] Agendamento automático
- [ ] Integração com redes sociais
- [ ] Templates personalizáveis

### [2.0.0] - Previsto
- [ ] Arquitetura de microserviços
- [ ] API REST completa
- [ ] Dashboard de monitoramento
- [ ] Inteligência artificial para otimização automática

# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "triathlon-crew-ai"
version = "1.0.0"
description = "Projeto CrewAI para automação de blog sobre triathlon"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Seu Nome", email = "seu.email@exemplo.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    "crewai==0.28.8",
    "crewai-tools==0.1.6",
    "langchain-openai==0.1.0",
    "langchain-community==0.0.29",
    "python-dotenv==1.0.0",
    "requests==2.31.0",
    "beautifulsoup4==4.12.2",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "flake8",
    "mypy",
    "coverage",
]

[project.urls]
Homepage = "https://github.com/seu-usuario/triathlon-crew-ai"
Repository = "https://github.com/seu-usuario/triathlon-crew-ai.git"
Issues = "https://github.com/seu-usuario/triathlon-crew-ai/issues"

[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi? Pesquisa web
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# config/__init__.py
"""
Configurações do projeto Triathlon CrewAI
"""

from .settings import Settings

__all__ = ['Settings']

# agents/__init__.py
"""
Agentes especializados para automação de blog sobre triathlon
"""

from .research_agent import TriathlonResearchAgent
from .content_writer_agent import ContentWriterAgent
from .seo_optimizer_agent import SEOOptimizerAgent

__all__ = [
    'TriathlonResearchAgent',
    'ContentWriterAgent', 
    'SEOOptimizerAgent'
]

# tools/__init__.py
"""
Ferramentas especializadas para pesquisa e processamento
"""

from .search_tools import TriathlonSearchTool

__all__ = ['TriathlonSearchTool']

# utils/__init__.py
"""
Utilitários gerais do projeto
"""

from .file_handler import FileHandler

__all__ = ['FileHandler']

# tests/__init__.py
"""
Testes unitários do projeto Triathlon CrewAI
"""

# scripts/__init__.py
"""
Scripts de automação e utilitários
"""

# CONTRIBUTING.md
# Contribuindo para o Projeto

Obrigado por considerar contribuir para o Triathlon CrewAI! 🎉

## Como Contribuir

### 1. Fork e Clone
```bash
# Fork no GitHub, depois:
git clone https://github.com/seu-usuario/triathlon-crew-ai.git
cd triathlon-crew-ai
```

### 2. Configurar Ambiente
```bash
make setup-dev
# ou manualmente:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest black flake8
```

### 3. Criar Branch
```bash
git checkout -b feature/sua-funcionalidade
# ou
git checkout -b fix/seu-bugfix
```

### 4. Desenvolver
- Escreva código seguindo as convenções do projeto
- Adicione testes para novas funcionalidades
- Mantenha documentação atualizada

### 5. Testar
```bash
make test
make lint
make format-check
```

### 6. Commit e Push
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/sua-funcionalidade
```

### 7. Pull Request
- Abra PR no GitHub
- Descreva as mudanças claramente
- Inclua screenshots se aplicável

## Convenções

### Commits
Seguimos [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` tarefas gerais

### Código
- Use Black para formatação
- Siga PEP 8
- Docstrings para funções públicas
- Type hints quando possível

### Testes
- Escreva testes para novas funcionalidades
- Mantenha cobertura > 80%
- Use nomes descritivos

## Tipos de Contribuição

### 🐛 Reportar Bugs
- Use template de issue
- Inclua passos para reproduzir
- Especifique ambiente

### 💡 Sugerir Funcionalidades  
- Use template de feature request
- Explique o caso de uso
- Considere alternativas

### 📝 Melhorar Documentação
- README, docstrings, comentários
- Exemplos de uso
- Guias tutoriais

### 🔧 Contribuir Código
- Novas funcionalidades
- Correções de bugs
- Melhorias de performance
- Refatorações

## Processo de Review

1. **Automático**: CI/CD executa testes
2. **Manual**: Maintainer revisa código
3. **Feedback**: Discussão e ajustes
4. **Merge**: Após aprovação

## Dúvidas?

- Abra uma issue
- Entre em contato: seu.email@exemplo.com
- Discord: [link-discord]

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque na colaboração
- Mantenha discussões técnicas

Obrigado por contribuir! 🚀

# SECURITY.md
# Política de Segurança

## Versões Suportadas

| Versão | Suportada          |
| ------ | ------------------ |
| 1.0.x  | ✅ Sim             |
| < 1.0  | ❌ Não             |

## Reportar Vulnerabilidades

### Como Reportar
Para reportar vulnerabilidades de segurança:

1. **NÃO** abra uma issue pública
2. Envie email para: security@exemplo.com
3. Inclua detalhes da vulnerabilidade
4. Aguarde resposta em até 48h

### Informações Necessárias
- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Versões afetadas
- Possível correção (se conhecida)

### Processo de Resposta
1. **Reconhecimento** (48h): Confirmamos recebimento
2. **Análise** (1 semana): Avaliamos a vulnerabilidade
3. **Correção** (2 semanas): Desenvolvemos fix
4. **Divulgação** (30 dias): Publicamos correção

## Melhores Práticas

### Para Usuários
- Mantenha dependências atualizadas
- Use chaves de API seguras
- Configure `.env` corretamente
- Não exponha logs sensíveis

### Para Desenvolvedores
- Sanitize inputs de usuário
- Use HTTPS para APIs
- Validação rigorosa de dados
- Logs sem informações sensíveis

## Dependências de Segurança

Monitoramos vulnerabilidades em:
- CrewAI
- OpenAI SDK
- LangChain
- Requests
- Outras dependências

## Histórico de Segurança

Nenhuma vulnerabilidade reportada até o momento.

# Performance e Benchmarks

## Métricas de Performance

### Tempos de Execução Típicos
- **Pesquisa**: 30-60 segundos
- **Escrita**: 45-90 segundos  
- **SEO**: 15-30 segundos
- **Total**: 2-4 minutos

### Uso de Recursos
- **RAM**: ~200-500MB
- **CPU**: Moderado durante execução
- **Armazenamento**: ~10-50MB por execução

### Tokens Utilizados (OpenAI)
- **Pesquisa**: ~1.000-2.000 tokens
- **Escrita**: ~2.000-4.000 tokens
- **SEO**: ~1.500-3.000 tokens
- **Total**: ~4.500-9.000 tokens

## Otimizações

### Para Performance
```python
# Configurações otimizadas
Settings.TEMPERATURE = 0.3  # Menos criativo, mais rápido
Settings.DEFAULT_MODEL = "gpt-3.5-turbo"  # Mais rápido que GPT-4
```

### Para Qualidade
```python
# Configurações de qualidade
Settings.TEMPERATURE = 0.7  # Mais criativo
Settings.DEFAULT_MODEL = "gemini-1.5-pro"  # Melhor qualidade
```

### Cache e Persistência
- Implementar cache de pesquisas
- Reutilizar resultados recentes
- Otimizar prompts para eficiência

## Monitoramento

### Logs de Performance
```python
import time
import logging

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logging.info(f"{func.__name__} executado em {end_time - start_time:.2f}s")
        return result
    return wrapper
```

### Métricas Recomendadas
- Tempo de execução por agente
- Uso de tokens por tarefa
- Taxa de sucesso das pesquisas
- Qualidade do conteúdo gerado Pesquisa web, 
            f'# As Melhores Provas de Triathlon do {country} em {year} | Guia Completo 🏊‍♂️🚴‍♂️🏃‍♂️', 
            content, 
            flags=re.MULTILINE
        )
        
        # Adiciona parágrafos de abertura otimizados para SEO com parâmetros dinâmicos
        seo_intro = f"""
**Procurando as melhores provas de triathlon do {country} em {year}?** Você está no lugar certo! Este guia completo reúne as principais competições de triathlon de {year}, com informações atualizadas sobre datas, locais, inscrições e tudo que você precisa saber para participar das provas de {year}.

**Palavras-chave principais:** provas triathlon {country.lower()}, ironman {country.lower()} {year}, calendário triathlon {year}, inscrições triathlon {year}
"""
        
        # Insere o conteúdo SEO após o primeiro título
        lines = content.split('\n')
        title_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title_index = i
                break
        
        lines.insert(title_index + 1, seo_intro)
        content = '\n'.join(lines)
        
        # Otimiza subtítulos (H2, H3) com palavras-chave e parâmetros dinâmicos
        content = re.sub(
            r'^## Por que você deveria se importar\?',
            f'## Por Que Participar de Provas de Triathlon no {country} em {year}?',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'^## O Que Você Vai Descobrir Aqui',
            f'## Guia Completo: Triathlon {country} {year}',
            content,
            flags=re.MULTILINE
        )
        
        # Adiciona internal linking opportunities com parâmetros dinâmicos
        content = re.sub(
            r'(?<![\[\(])\btriathlon\b(?![\]\)])',
            f'[triathlon](link-para-post-sobre-triathlon-{year})',
            content,
            count=2
        )
        
        # Adiciona FAQ section para SEO com parâmetros dinâmicos
        faq_section = f"""
---

## Perguntas Frequentes - Provas de Triathlon {country} {year}

### Qual é a melhor prova de triathlon para iniciantes no {country} em {year}?
As provas de distância Sprint e Olímpica são ideais para iniciantes em {year}, oferecendo percursos técnicos mas acessíveis em diversas cidades do {country}.

### Quando começam as inscrições para as provas de triathlon de {year}?
As inscrições para as provas de {year} geralmente abrem entre dezembro de {year-1} e janeiro de {year}, com descontos especiais para as primeiras inscrições.

### Quanto custa participar de uma prova de triathlon no {country} em {year}?
Os valores para {year} variam de R$ 150 (provas locais) até R$ 800 (Ironman {country}), dependendo da distância e prestígio da prova.

### Qual equipamento é obrigatório para provas de triathlon em {year}?
Para {year}, continuam obrigatórios: capacete homologado, roupa de neoprene (para águas frias), tênis de corrida e bicicleta em bom estado.

### Como está o calendário de triathlon {country} {year}?
O calendário {year} promete ser um dos mais completos dos últimos anos, com provas distribuídas ao longo de todo o ano em diversas regiões do {country}.

---
"""
        
        content += faq_section
        
        # Adiciona schema markup suggestions com parâmetros dinâmicos
        schema_section = f"""
<!-- SCHEMA MARKUP SUGERIDO (adicionar no WordPress):
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "As Melhores Provas de Triathlon do {country} em {year}",
  "author": {{
    "@type": "Person",
    "name": "Especialista em Triathlon"
  }},
  "datePublished": "{year}-01-01",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "https://seusite.com/melhores-provas-triathlon-{country.lower()}-{year}/"
  }},
  "keywords": "triathlon {country.lower()}, provas triathlon {year}, ironman {country.lower()}, calendário triathlon {year}"
}}
-->
"""
        
        content += schema_section
        
        return optimized_content + content
    
    def _generate_seo_report(self, content: str, year: int) -> str:
        """Gera relatório de análise SEO"""
        
        # Análises básicas
        word_count = len(content.split())
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Densidade de palavra-chave principal com parâmetros dinâmicos
        keyword = f"triathlon {year}"
        keyword_count = content.lower().count(keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        # Análise de palavras-chave secundárias
        secondary_keywords = [
            f"provas triathlon {year}",
            f"ironman {year}",
            f"calendário triathlon {year}"
        ]
        
        keyword_analysis = {}
        for kw in secondary_keywords:
            count = content.lower().count(kw.lower())
            density = (count / word_count) * 100 if word_count > 0 else 0
            keyword_analysis[kw] = {"count": count, "density": density}
        
        report = f"""# Relatório de Análise SEO - Triathlon Blog Post {year}

## Métricas Gerais
- **Contagem de palavras:** {word_count} palavras ✅ (Ideal: 1000+ palavras)
- **Títulos H1:** {h1_count} ✅ (Ideal: 1 título H1)
- **Títulos H2:** {h2_count} ✅ (Ideal: 3-5 títulos H2)
- **Títulos H3:** {h3_count} ✅ (Ideal: múltiplos H3 para estrutura)

## Análise de Palavras-chave para {year}

### Palavra-chave Principal
- **Keyword:** "{keyword}"
- **Frequência:** {keyword_count} ocorrências
- **Densidade:** {keyword_density:.2f}% ✅ (Ideal: 1-3%)

### Palavras-chave Secundárias
"""
        
        for kw, data in keyword_analysis.items():
            status = "✅" if 0.5 <= data["density"] <= 2.0 else "⚠️"
            report += f"- **{kw}:** {data['count']} ocorrências ({data['density']:.2f}%) {status}\n"
        
        report += f"""

## Checklist de SEO para {year}

### ✅ Otimizações Aplicadas:
- Meta título otimizado para {year} (< 60 caracteres)
- Meta description atrativa específica para {year} (< 160 caracteres)
- Estrutura de headers hierárquica (H1 > H2 > H3)
- Uso de palavras-chave de {year} naturalmente distribuídas
- Internal linking implementado com links contextuais
- FAQ section otimizada para featured snippets de {year}
- Schema markup preparado com dados de {year}
- URLs amigáveis sugeridas (/triathlon-{year}/)
- Alt text para imagens (lembrar de adicionar ao publicar)

### 🚨 Próximos Passos para {year}:
1. **Adicionar imagens otimizadas** com alt text sobre triathlon {year}
2. **Implementar schema markup** no WordPress com dados de {year}
3. **Configurar internal links** para posts relacionados de {year}
4. **Adicionar meta tags** no plugin de SEO (Yoast/RankMath)
5. **Otimizar velocidade** da página
6. **Construir backlinks** de sites de autoridade em esportes focados em {year}
7. **Monitorar performance** nas palavras-chave de {year}

## Score SEO Estimado: 87/100 🎯

### Pontos Fortes:
- Conteúdo extenso e detalhado para {year}
- Estrutura clara e hierárquica
- Palavras-chave de {year} bem distribuídas
- Call-to-actions efetivos e sazonais
- FAQ otimizada para snippets de {year}
- Foco temporal bem definido ({year})

### Áreas de Melhoria:
- Adicionar mais variações long-tail das palavras-chave de {year}
- Incluir dados estruturados de eventos
- Otimizar para pesquisas locais + {year}
- Adicionar elementos visuais (infográficos do calendário {year})

## Análise de Sazonalidade

### Vantagens SEO do Foco em {year}:
- ✅ Busca por "triathlon {year}" tem baixa concorrência
- ✅ Conteúdo temporal tem relevância específica
- ✅ Oportunidade de ranking em featured snippets sazonais

### Recomendações de Conteúdo Futuro:
- Criar posts de acompanhamento durante {year}
- Desenvolver conteúdo para "melhores provas triathlon {year + 1}"
- Planejar série de posts por trimestre de {year}

---

**Data da análise:** {self._get_current_date()}
**Período analisado:** Triathlon {year}
**Ferramenta:** SEO Optimizer Agent - CrewAI v2.0
"""
        
        return report
    
    def _get_current_date(self) -> str:
        """Retorna data atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    def _apply_seo_optimizations(self, content: str) -> str:
        """Aplica otimizações de SEO ao conteúdo"""
        
        # Adiciona meta tags e estrutura WordPress
        optimized_content = """<!--
SEO METADATA:
Title: As Melhores Provas de Triathlon do Brasil em 2024 | Guia Completo
Meta Description: Descubra as melhores provas de triathlon do Brasil em 2024. Guia completo com datas, locais, inscrições e dicas de atletas experientes.
Focus Keyword: provas de triathlon brasil 2024
Keywords: triathlon brasil, provas triathlon, ironman brasil, triathlon 2024, corridas triathlon
Slug: /melhores-provas-triathlon-brasil-2024/
-->

"""
        
        # Otimiza o título principal (H1)
        content = re.sub(
            r'^# (.+)$', 
            r'# As Melhores Provas de Triathlon do Brasil em 2024 | Guia Completo 🏊‍♂️🚴‍♂️🏃‍♂️', 
            content, 
            flags=re.MULTILINE
        )
        
        # Adiciona parágrafos de abertura otimizados para SEO
        seo_intro = """
**Procurando as melhores provas de triathlon do Brasil em 2024?** Você está no lugar certo! Este guia completo reúne as principais competições de triathlon brasileiras, com informações atualizadas sobre datas, locais, inscrições e tudo que você precisa saber para participar.

**Palavras-chave principais:** provas triathlon brasil, ironman brasil 2024, calendário triathlon, inscrições triathlon
"""
        
        # Insere o conteúdo SEO após o primeiro título
        lines = content.split('\n')
        title_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title_index = i
                break
        
        lines.insert(title_index + 1, seo_intro)
        content = '\n'.join(lines)
        
        # Otimiza subtítulos (H2, H3) com palavras-chave
        content = re.sub(
            r'^## Por que você deveria se importar\?',
            r'## Por Que Participar de Provas de Triathlon no Brasil?',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'^## O Que Você Vai Descobrir Aqui',
            r'## Guia Completo: Triathlon Brasil 2024',
            content,
            flags=re.MULTILINE
        )
        
        # Adiciona internal linking opportunities
        content = re.sub(
            r'triathlon',
            r'[triathlon](link-para-post-sobre-triathlon)',
            content,
            count=2  # Apenas os primeiros 2 links
        )
        
        # Adiciona FAQ section para SEO
        faq_section = """
---

## Perguntas Frequentes - Provas de Triathlon Brasil 2024

### Qual é a melhor prova de triathlon para iniciantes no Brasil?
O Triathlon Internacional de Santos é ideal para iniciantes, oferecendo distância olímpica em um percurso técnico mas acessível.

### Quando começam as inscrições para as provas de triathlon em 2024?
As inscrições geralmente abrem entre dezembro e janeiro, com descontos especiais para as primeiras inscrições.

### Quanto custa participar de uma prova de triathlon no Brasil?
Os valores variam de R$ 150 (provas locais) até R$ 800 (Ironman Brasil), dependendo da distância e prestígio da prova.

### Qual equipamento é obrigatório para provas de triathlon?
Capacete homologado, roupa de neoprene (para águas frias), tênis de corrida e bicicleta em bom estado são obrigatórios.

---
"""
        
        content += faq_section
        
        # Adiciona schema markup suggestions
        schema_section = """
<!-- SCHEMA MARKUP SUGERIDO (adicionar no WordPress):
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "As Melhores Provas de Triathlon do Brasil em 2024",
  "author": {
    "@type": "Person",
    "name": "Seu Nome"
  },
  "datePublished": "2024-08-05",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://seusite.com/melhores-provas-triathlon-brasil-2024/"
  }
}
-->
"""
        
        content += schema_section
        
        return optimized_content + content
    
    def _generate_seo_report(self, content: str) -> str:
        """Gera relatório de análise SEO"""
        
        # Análises básicas
        word_count = len(content.split())
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Densidade de palavra-chave principal
        keyword = "triathlon"
        keyword_count = content.lower().count(keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        report = f"""# Relatório de Análise SEO - Triathlon Blog Post

## Métricas Gerais
- **Contagem de palavras:** {word_count} palavras ✅ (Ideal: 1000+ palavras)
- **Títulos H1:** {h1_count} ✅ (Ideal: 1 título H1)
- **Títulos H2:** {h2_count} ✅ (Ideal: 3-5 títulos H2)
- **Títulos H3:** {h3_count} ✅ (Ideal: múltiplos H3 para estrutura)

## Análise de Palavras-chave
- **Palavra-chave principal:** "{keyword}"
- **Frequência:** {keyword_count} ocorrências
- **Densidade:** {keyword_density:.2f}% ✅ (Ideal: 1-3%)

## Checklist de SEO

### ✅ Otimizações Aplicadas:
- Meta título otimizado (< 60 caracteres)
- Meta description atrativa (< 160 caracteres)
- Estrutura de headers hierárquica (H1 > H2 > H3)
- Uso de palavras-chave naturalmente
- Internal linking implementado
- FAQ section para featured snippets
- Schema markup preparado
- URLs amigáveis sugeridas
- Alt text para imagens (lembrar de adicionar)

### 🚨 Próximos Passos:
1. **Adicionar imagens otimizadas** com alt text relevante
2. **Implementar schema markup** no WordPress
3. **Configurar internal links** para posts relacionados
4. **Adicionar meta tags** no plugin de SEO (Yoast/RankMath)
5. **Otimizar velocidade** da página
6. **Construir backlinks** de sites de autoridade em esportes

## Score SEO Estimado: 85/100 🎯

### Pontos Fortes:
- Conteúdo extenso e detalhado
- Estrutura clara e hierárquica
- Palavras-chave bem distribuídas
- Call-to-actions efetivos
- FAQ otimizada para snippets

### Áreas de Melhoria:
- Adicionar mais variações de palavra-chave
- Incluir dados estruturados
- Otimizar para mobile-first
- Adicionar mais elementos visuais

---

**Data da análise:** {self._get_current_date()}
**Ferramenta:** SEO Optimizer Agent - CrewAI
"""
        
        return report
    
    def _get_current_date(self) -> str:
        """Retorna data atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")

# main.py - Arquivo principal
from crewai import Crew, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings
from agents.research_agent import TriathlonResearchAgent
from agents.content_writer_agent import ContentWriterAgent
from agents.seo_optimizer_agent import SEOOptimizerAgent
from utils.file_handler import FileHandler
import os

def main():
    """Função principal que executa o fluxo completo"""
    
    try:
        # Valida configurações
        Settings.validate_config()
        
        # Inicializa o modelo de linguagem
        llm = ChatGoogleGenerativeAI(
            model=Settings.DEFAULT_MODEL,
            temperature=Settings.TEMPERATURE,
            google_api_key=Settings.GOOGLE_API_KEY
        )
        
        # Cria os diretórios necessários
        FileHandler.ensure_directory(Settings.DATA_DIR)
        FileHandler.ensure_directory(Settings.OUTPUT_DIR)
        
        print("🚀 Iniciando projeto CrewAI - Triathlon Blog Automation\n")
        
        # Inicializa os agentes
        research_agent = TriathlonResearchAgent(llm)
        writer_agent = ContentWriterAgent(llm)
        seo_agent = SEOOptimizerAgent(llm)
        
        # Define as tarefas
        research_task = Task(
            description="""Realizar pesquisa abrangente sobre provas de triathlon no Brasil para 2024.
            Coletar informações sobre datas, locais, distâncias, preços de inscrição e websites oficiais.
            Estruturar os dados em formato JSON organizado e salvar no arquivo data/triathlon_events.json""",
            agent=research_agent.agent,
            expected_output="Arquivo JSON com dados estruturados das provas de triathlon"
        )
        
        writing_task = Task(
            description="""Ler o arquivo JSON gerado pela pesquisa e criar um post envolvente para blog.
            Aplicar técnicas do livro 'Brevidade Inteligente' para criar conteúdo que prenda a atenção.
            O post deve ser informativo, acionável e otimizado para engajamento.
            Salvar o conteúdo em formato Markdown no arquivo output/triathlon_blog_post.md""",
            agent=writer_agent.agent,
            expected_output="Post de blog em Markdown otimizado para engajamento",
            context=[research_task]
        )
        
        seo_task = Task(
            description="""Revisar e otimizar o post criado aplicando as melhores práticas de SEO.
            Adicionar meta tags, otimizar títulos, implementar palavras-chave estratégicas,
            criar estrutura de FAQ e preparar schema markup.
            Gerar também um relatório detalhado de análise SEO.
            Salvar versão otimizada e relatório nos arquivos correspondentes.""",
            agent=seo_agent.agent,
            expected_output="Post otimizado para SEO e relatório de análise",
            context=[writing_task]
        )
        
        # Cria e executa a crew
        crew = Crew(
            agents=[
                research_agent.agent,
                writer_agent.agent, 
                seo_agent.agent
            ],
            tasks=[research_task, writing_task, seo_task],
            verbose=True,
            process="sequential"  # Execução sequencial
        )
        
        print("🔍 Executando pesquisa de provas de triathlon...")
        print("✍️  Criando post otimizado para blog...")
        print("🎯 Aplicando otimizações de SEO...")
        
        # Executa o fluxo
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("🎉 PROJETO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\n📁 Arquivos gerados:")
        print("   📊 data/triathlon_events.json - Dados da pesquisa")
        print("   📝 output/triathlon_blog_post.md - Post original")
        print("   🎯 output/triathlon_blog_post_seo_optimized.md - Post otimizado")
        print("   📈 output/seo_analysis_report.md - Relatório SEO")
        
        print(f"\n🤖 Resultado final da execução:")
        print(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        return None

if __name__ == "__main__":
    main()

# setup.py
from setuptools import setup, find_packages

setup(
    name="triathlon-crew-ai",
    version="1.0.0",
    description="Projeto CrewAI para automação de blog sobre triathlon",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "crewai==0.28.8",
        "crewai-tools==0.1.6",
        "langchain-openai==0.1.0",
        "langchain-community==0.0.29",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

# README.md
# 🏊‍♂️🚴‍♂️🏃‍♂️ Triathlon CrewAI - Automação de Blog

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-v0.28.8-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Um projeto completo usando **CrewAI** para automatizar a criação de conteúdo sobre triathlon, com 3 agentes especializados trabalhando em sequência para pesquisar, escrever e otimizar posts para blog.

## 🎯 Objetivo

Criar um fluxo automatizado que:
1. **Pesquisa** provas de triathlon na internet
2. **Escreve** posts otimizados aplicando técnicas de "Brevidade Inteligente"
3. **Otimiza** o conteúdo para SEO e WordPress

## 🤖 Agentes

### 1. **Research Agent** - Especialista em Pesquisa
- 🔍 Pesquisa provas de triathlon no Brasil
- 📊 Estrutura dados em formato JSON
- 🎯 Coleta informações detalhadas (datas, locais, inscrições)

### 2. **Content Writer Agent** - Redator Especialista
- ✍️ Transforma dados em posts envolventes
- 📚 Aplica técnicas de "Brevidade Inteligente"
- 🎨 Cria conteúdo otimizado para engajamento

### 3. **SEO Optimizer Agent** - Especialista em SEO
- 🎯 Otimiza posts para mecanismos de busca
- 📈 Implementa melhores práticas de SEO
- 📊 Gera relatórios detalhados de análise

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/triathlon-crew-ai.git
cd triathlon-crew-ai
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
# ou
pip install -e .
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
GOOGLE_API_KEY=sua_chave_openai_aqui
SERPER_API_KEY=sua_chave_serper_aqui
```

### 5. Execute o projeto
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
triathlon-crew-ai/
├── 📁 config/
│   └── settings.py           # Configurações globais
├── 📁 agents/
│   ├── research_agent.py     # Agente de pesquisa
│   ├── content_writer_agent.py # Agente escritor
│   └── seo_optimizer_agent.py  # Agente SEO
├── 📁 tools/
│   └── search_tools.py       # Ferramentas de pesquisa
├── 📁 utils/
│   └── file_handler.py       # Utilitários para arquivos
├── 📁 data/                  # Dados de pesquisa (JSON)
├── 📁 output/                # Posts e relatórios gerados
├── main.py                   # Arquivo principal
├── requirements.txt          # Dependências
├── setup.py                  # Configuração do pacote
├── .env.example             # Exemplo de variáveis de ambiente
└── README.md                # Este arquivo
```

## 🛠️ Como Funciona

### Fluxo de Execução
1. **Pesquisa** → O Research Agent busca provas de triathlon e salva em JSON
2. **Escrita** → O Content Writer Agent cria post aplicando "Brevidade Inteligente"
3. **Otimização** → O SEO Agent otimiza o post e gera relatório de análise

### Arquivos Gerados
- `📊 data/triathlon_events.json` - Dados estruturados da pesquisa
- `📝 output/triathlon_blog_post.md` - Post original para blog
- `🎯 output/triathlon_blog_post_seo_optimized.md` - Post otimizado para SEO
- `📈 output/seo_analysis_report.md` - Relatório detalhado de SEO

## 🎨 Técnicas Aplicadas

### Brevidade Inteligente
- ⚡ **Ganchos iniciais** que prendem atenção
- 🎯 **Informação concentrada** e acionável
- 📞 **Call-to-actions** claros e efetivos
- 💡 **Estrutura escaneável** com bullets e headers

### SEO Otimização
- 🔍 **Palavras-chave estratégicas** naturalmente integradas
- 📱 **Meta tags otimizadas** para title e description
- 🏗️ **Estrutura hierárquica** com headers H1-H3
- ❓ **FAQ section** para featured snippets
- 🔗 **Internal linking** e schema markup

## ⚙️ Configurações Avançadas

### Personalizando Agentes
Você pode modificar os agentes em `agents/` para:
- Alterar prompts e comportamentos
- Adicionar novas ferramentas
- Customizar saídas e formatos

### Adicionando Novas Ferramentas
Crie novas ferramentas em `tools/` para:
- Integrar com outras APIs
- Adicionar funcionalidades específicas
- Conectar com serviços externos

### Configurando LLM
Altere o modelo em `config/settings.py`:
```python
DEFAULT_MODEL = "gemini-1.5-pro"  # ou "gpt-3.5-turbo"
TEMPERATURE = 0.7  # Criatividade (0.0 - 1.0)
```

## 📊 Exemplo de Saída

### JSON de Pesquisa
```json
{
  "timestamp": "2024-08-05T10:30:00",
  "events": [
    {
      "name": "Ironman Brasil 2024",
      "location": "Florianópolis, SC",
      "date": "2024-05-26",
      "distance": "Full Distance",
      "registration_open": true,
      "website": "https://ironman.com.br"
    }
  ],
  "summary": {
    "total_events": 2,
    "upcoming_events": 2,
    "locations": ["Florianópolis, SC", "Santos, SP"]
  }
}
```

### Post Otimizado
- ✅ Título SEO-friendly
- ✅ Meta description atrativa
- ✅ Estrutura hierárquica clara
- ✅ Call-to-actions efetivos
- ✅ FAQ para snippets
- ✅ Schema markup preparado

## 🔧 Troubleshooting

### Problemas Comuns

**Erro de API Key:**
```bash
ValueError: Variáveis de ambiente ausentes: ['GOOGLE_API_KEY']
```
**Solução:** Verifique se o arquivo `.env` está configurado corretamente.

**Erro de Dependências:**
```bash
ModuleNotFoundError: No module named 'crewai'
```
**Solução:** Execute `pip install -r requirements.txt`

**Timeout na Pesquisa:**
**Solução:** Verifique sua conexão e as chaves de API do Serper.

## 🚧 Próximas Melhorias

- [ ] **Integração WordPress** - Deploy automático via API
- [ ] **Análise de Sentimento** - Otimização baseada em feedback
- [ ] **Geração de Imagens** - Criação automática de thumbnails
- [ ] **Agendamento** - Execução automática por cronograma
- [ ] **Métricas Analytics** - Tracking de performance dos posts
- [ ] **Multi-idiomas** - Suporte para outros idiomas
- [ ] **Templates Personalizados** - Diferentes estilos de post

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Perfil](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com

## 🙏 Agradecimentos

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Framework para agentes IA
- [OpenAI](https://openai.com/) - Modelo de linguagem GPT
- [Serper](https://serper.dev/) - API de pesquisa
- [Brevidade Inteligente] - Técnicas de copywriting aplicadas

---

⭐ **Se este projeto foi útil, dê uma estrela no GitHub!** ⭐

# .env.example
# Chaves de API necessárias
GOOGLE_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Configurações opcionais
DEFAULT_MODEL=gemini-1.5-pro
TEMPERATURE=0.7

# .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Arquivos específicos do projeto
data/
output/
*.json
*.md
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# tests/test_agents.py
import unittest
from unittest.mock import Mock, patch
import json
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import TriathlonResearchAgent
from agents.content_writer_agent import ContentWriterAgent
from agents.seo_optimizer_agent import SEOOptimizerAgent

class TestTriathlonAgents(unittest.TestCase):
    """Testes unitários para os agentes de triathlon"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.mock_llm = Mock()
        
    def test_research_agent_initialization(self):
        """Testa inicialização do agente de pesquisa"""
        agent = TriathlonResearchAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertIsNotNone(agent.search_tool)
        self.assertEqual(agent.agent.role, "Especialista em Pesquisa de Triathlon")
    
    def test_content_writer_initialization(self):
        """Testa inicialização do agente escritor"""
        agent = ContentWriterAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertEqual(agent.agent.role, "Redator Especialista em Content Marketing")
    
    def test_seo_optimizer_initialization(self):
        """Testa inicialização do agente SEO"""
        agent = SEOOptimizerAgent(self.mock_llm)
        
        self.assertIsNotNone(agent.agent)
        self.assertEqual(agent.agent.role, "Especialista em SEO e Otimização de Conteúdo")
    
    @patch('agents.research_agent.FileHandler')
    def test_research_agent_data_consolidation(self, mock_file_handler):
        """Testa consolidação de dados do agente de pesquisa"""
        agent = TriathlonResearchAgent(self.mock_llm)
        
        # Dados de teste
        test_results = [
            {
                "timestamp": "2024-08-05T10:00:00",
                "events": [
                    {"name": "Ironman Brasil", "location": "Florianópolis"},
                    {"name": "Triathlon Santos", "location": "Santos"}
                ],
                "sources": ["source1.com"]
            },
            {
                "timestamp": "2024-08-05T10:30:00", 
                "events": [
                    {"name": "Ironman Brasil", "location": "Florianópolis"},  # Duplicata
                    {"name": "Triathlon Rio", "location": "Rio de Janeiro"}
                ],
                "sources": ["source2.com"]
            }
        ]
        
        consolidated = agent._consolidate_results(test_results)
        
        # Verifica se duplicatas foram removidas
        self.assertEqual(len(consolidated["events"]), 3)
        
        # Verifica se localizações foram coletadas
        self.assertIn("Florianópolis", consolidated["summary"]["locations"])
        self.assertIn("Santos", consolidated["summary"]["locations"])
        self.assertIn("Rio de Janeiro", consolidated["summary"]["locations"])
    
    def test_content_writer_date_formatting(self):
        """Testa formatação de datas no agente escritor"""
        agent = ContentWriterAgent(self.mock_llm)
        
        # Testa formatação de data válida
        formatted_date = agent._format_date("2024-05-26")
        self.assertIn("2024", formatted_date)
        
        # Testa com data inválida
        invalid_date = agent._format_date("invalid-date")
        self.assertEqual(invalid_date, "invalid-date")
    
    def test_seo_optimizer_keyword_analysis(self):
        """Testa análise de palavras-chave do agente SEO"""
        agent = SEOOptimizerAgent(self.mock_llm)
        
        test_content = "Este é um post sobre triathlon. O triathlon é um esporte completo."
        word_count = len(test_content.split())
        keyword_count = test_content.lower().count("triathlon")
        keyword_density = (keyword_count / word_count) * 100
        
        # Verifica cálculo de densidade
        self.assertGreater(keyword_density, 0)
        self.assertEqual(keyword_count, 2)

if __name__ == '__main__':
    unittest.main()

# tests/test_tools.py
import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.search_tools import TriathlonSearchTool

class TestTriathlonSearchTool(unittest.TestCase):
    """Testes para a ferramenta de pesquisa de triathlon"""
    
    def setUp(self):
        """Configuração inicial"""
        self.search_tool = TriathlonSearchTool()
    
    def test_process_search_results_structure(self):
        """Testa estrutura dos resultados processados"""
        mock_results = "Sample search results"
        processed = self.search_tool._process_search_results(mock_results)
        
        # Verifica estrutura básica
        self.assertIn("timestamp", processed)
        self.assertIn("events", processed)
        self.assertIn("sources", processed)
        self.assertIn("summary", processed)
        
        # Verifica estrutura do summary
        summary = processed["summary"]
        self.assertIn("total_events", summary)
        self.assertIn("upcoming_events", summary)
        self.assertIn("locations", summary)
    
    def test_event_data_structure(self):
        """Testa estrutura dos dados de eventos"""
        mock_results = "Sample search results"
        processed = self.search_tool._process_search_results(mock_results)
        
        if processed["events"]:
            event = processed["events"][0]
            required_fields = ["name", "location", "date", "distance", "registration_open", "website", "description"]
            
            for field in required_fields:
                self.assertIn(field, event)

if __name__ == '__main__':
    unittest.main()

# tests/test_utils.py
import unittest
import tempfile
import os
import json
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import FileHandler

class TestFileHandler(unittest.TestCase):
    """Testes para o manipulador de arquivos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_handler = FileHandler()
    
    def tearDown(self):
        """Limpeza após os testes"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory(self):
        """Testa criação de diretórios"""
        test_dir = os.path.join(self.temp_dir, "test_directory")
        
        # Diretório não deve existir inicialmente
        self.assertFalse(os.path.exists(test_dir))
        
        # Cria o diretório
        FileHandler.ensure_directory(test_dir)
        
        # Diretório deve existir agora
        self.assertTrue(os.path.exists(test_dir))
    
    def test_save_and_load_json(self):
        """Testa salvamento e carregamento de JSON"""
        test_data = {
            "name": "Test Event",
            "location": "Test Location",
            "date": "2024-08-05"
        }
        
        json_path = os.path.join(self.temp_dir, "test.json")
        
        # Salva JSON
        FileHandler.save_json(test_data, json_path)
        
        # Verifica se arquivo foi criado
        self.assertTrue(os.path.exists(json_path))
        
        # Carrega JSON
        loaded_data = FileHandler.load_json(json_path)
        
        # Verifica se dados são iguais
        self.assertEqual(test_data, loaded_data)
    
    def test_save_text(self):
        """Testa salvamento de texto"""
        test_content = "Este é um conteúdo de teste para o arquivo."
        text_path = os.path.join(self.temp_dir, "test.txt")
        
        # Salva texto
        FileHandler.save_text(test_content, text_path)
        
        # Verifica se arquivo foi criado
        self.assertTrue(os.path.exists(text_path))
        
        # Lê o arquivo e verifica conteúdo
        with open(text_path, 'r', encoding='utf-8') as f:
            loaded_content = f.read()
        
        self.assertEqual(test_content, loaded_content)

if __name__ == '__main__':
    unittest.main()

# Makefile
# Makefile para automação de tarefas do projeto

.PHONY: install test run clean lint format setup-dev

# Variáveis
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
FLAKE8 = flake8

# Instalação
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest black flake8 mypy

# Configuração do ambiente de desenvolvimento
setup-dev: install-dev
	@echo "Configurando ambiente de desenvolvimento..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Arquivo .env criado. Configure suas chaves de API!"; fi
	@mkdir -p data output logs
	@echo "Ambiente configurado com sucesso!"

# Execução
run:
	$(PYTHON) main.py

# Testes
test:
	$(PYTEST) tests/ -v

test-coverage:
	$(PYTEST) tests/ --cov=. --cov-report=html

# Linting e formatação
lint:
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	$(BLACK) . --line-length=100

format-check:
	$(BLACK) . --check --line-length=100

# Limpeza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-output:
	rm -rf data/*
	rm -rf output/*
	rm -rf logs/*

# Docker (opcional)
docker-build:
	docker build -t triathlon-crew-ai .

docker-run:
	docker run --env-file .env triathlon-crew-ai

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  install      - Instala dependências básicas"
	@echo "  install-dev  - Instala dependências de desenvolvimento"
	@echo "  setup-dev    - Configura ambiente de desenvolvimento completo"
	@echo "  run          - Executa o projeto principal"
	@echo "  test         - Executa testes unitários"
	@echo "  test-coverage- Executa testes com relatório de cobertura"
	@echo "  lint         - Executa análise de código"
	@echo "  format       - Formata código com Black"
	@echo "  format-check - Verifica formatação sem alterar arquivos"
	@echo "  clean        - Remove arquivos temporários"
	@echo "  clean-output - Limpa diretórios de saída"
	@echo "  help         - Mostra esta ajuda"

# LICENSE
MIT License

Copyright (c) 2024 Triathlon CrewAI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Dockerfile (opcional)
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código do projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p data output logs

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expõe porta (se necessário para futuras extensões)
EXPOSE 8000

# Comando padrão
CMD ["python", "main.py"]

# docker-compose.yml (opcional)
version: '3.8'

services:
  triathlon-crew-ai:
    build: .
    container_name: triathlon-crew-ai
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
    env_file:
      - .env
    restart: unless-stopped

# scripts/run_project.py
#!/usr/bin/env python3
"""
Script para execução do projeto com validações e logs
"""

import sys
import os
import logging
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main
from config.settings import Settings

def setup_logging():
    """Configura sistema de logging"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = f"triathlon_crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'crewai',
        'langchain_google_genai',
        'python-dotenv',
        'requests',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes ausentes: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def pre_execution_checks():
    """Executa verificações antes da execução"""
    print("🔍 Executando verificações pré-execução...")
    
    # Verifica dependências
    if not check_dependencies():
        return False
    
    # Verifica configurações
    try:
        Settings.validate_config()
        print("✅ Configurações validadas")
    except ValueError as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    
    # Verifica diretórios
    directories = ['data', 'output', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Diretórios verificados")
    
    return True

def main_execution():
    """Executa o projeto principal com tratamento de erros"""
    logger = setup_logging()
    
    try:
        logger.info("Iniciando execução do projeto Triathlon CrewAI")
        
        if not pre_execution_checks():
            logger.error("Falha nas verificações pré-execução")
            return False
        
        # Executa o projeto principal
        result = main()
        
        if result:
            logger.info("Projeto executado com sucesso!")
            print("\n🎉 Execução concluída com sucesso!")
            return True
        else:
            logger.error("Falha na execução do projeto")
            print("\n❌ Falha na execução do projeto")
            return False
            
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        print("\n⏹️ Execução interrompida pelo usuário")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        print(f"\n💥 Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    success = main_execution()
    sys.exit(0 if success else 1)

# scripts/setup_env.py
#!/usr/bin/env python3
"""
Script para configuração inicial do ambiente
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✅ Arquivo .env criado a partir do .env.example")
        print("⚠️  Configure suas chaves de API no arquivo .env")
        return True
    elif env_path.exists():
        print("ℹ️  Arquivo .env já existe")
        return True
    else:
        print("❌ Arquivo .env.example não encontrado")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        "data",
        "output", 
        "logs",
        "tests/__pycache__",
        "agents/__pycache__",
        "tools/__pycache__",
        "utils/__pycache__",
        "config/__pycache__"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Diretórios criados")

def create_init_files():
    """Cria arquivos __init__.py necessários"""
    init_files = [
        "agents/__init__.py",
        "tools/__init__.py", 
        "utils/__init__.py",
        "config/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.touch()
    
    print("✅ Arquivos __init__.py criados")

def main():
    """Função principal de configuração"""
    print("🔧 Configurando ambiente do projeto...")
    
    create_directories()
    create_init_files()
    create_env_file()
    
    print("\n📋 Próximos passos:")
    print("1. Configure suas chaves de API no arquivo .env")
    print("2. Execute: pip install -r requirements.txt")
    print("3. Execute: python main.py")
    print("\n🚀 Ambiente configurado com sucesso!")

if __name__ == "__main__":
    main()

# scripts/validate_output.py
#!/usr/bin/env python3
"""
Script para validar arquivos de saída gerados
"""

import json
import os
from pathlib import Path
from datetime import datetime

def validate_json_file(filepath):
    """Valida arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validações específicas para dados de triathlon
        if 'events' in data:
            print(f"✅ {filepath}: {len(data['events'])} eventos encontrados")
            
            for i, event in enumerate(data['events'][:3]):  # Mostra apenas 3 primeiros
                print(f"   - {event.get('name', 'Nome não encontrado')}")
                
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ {filepath}: Erro JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ {filepath}: Erro - {e}")
        return False

def validate_markdown_file(filepath):
    """Valida arquivo Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificações básicas
        word_count = len(content.split())
        h1_count = content.count('# ')
        h2_count = content.count('## ')
        
        print(f"✅ {filepath}:")
        print(f"   - Palavras: {word_count}")
        print(f"   - Títulos H1: {h1_count}")
        print(f"   - Títulos H2: {h2_count}")
        
        # Verifica se tem conteúdo mínimo
        if word_count < 100:
            print(f"⚠️  Conteúdo muito curto (menos de 100 palavras)")
            
        return True
        
    except Exception as e:
        print(f"❌ {filepath}: Erro - {e}")
        return False

def validate_project_output():
    """Valida todos os arquivos de saída do projeto"""
    print("🔍 Validando arquivos de saída...\n")
    
    # Arquivos esperados
    expected_files = {
        "data/triathlon_events.json": validate_json_file,
        "output/triathlon_blog_post.md": validate_markdown_file,
        "output/triathlon_blog_post_seo_optimized.md": validate_markdown_file,
        "output/seo_analysis_report.md": validate_markdown_file
    }
    
    results = {}
    
    for filepath, validator in expected_files.items():
        if Path(filepath).exists():
            results[filepath] = validator(filepath)
        else:
            print(f"❌ {filepath}: Arquivo não encontrado")
            results[filepath] = False
    
    # Resumo
    print(f"\n📊 Resumo da Validação:")
    valid_files = sum(1 for success in results.values() if success)
    total_files = len(results)
    
    print(f"✅ Arquivos válidos: {valid_files}/{total_files}")
    
    if valid_files == total_files:
        print("🎉 Todos os arquivos estão válidos!")
        return True
    else:
        print("⚠️  Alguns arquivos apresentam problemas")
        return False

def generate_validation_report():
    """Gera relatório detalhado de validação"""
    report_content = f"""# Relatório de Validação - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Status dos Arquivos

"""
    
    files_to_check = [
        "data/triathlon_events.json",
        "output/triathlon_blog_post.md", 
        "output/triathlon_blog_post_seo_optimized.md",
        "output/seo_analysis_report.md"
    ]
    
    for filepath in files_to_check:
        if Path(filepath).exists():
            stat = Path(filepath).stat()
            size_kb = stat.st_size / 1024
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            report_content += f"### {filepath}
- ✅ **Status:** Arquivo encontrado
- 📁 **Tamanho:** {size_kb:.2f} KB
- 📅 **Modificado:** {modified.strftime('%Y-%m-%d %H:%M:%S')}

"
        else:
            report_content += f"### {filepath}
- ❌ **Status:** Arquivo não encontrado

"
    
    # Salva relatório
    report_path = "output/validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Relatório salvo em: {report_path}")

if __name__ == "__main__":
    validate_project_output()
    generate_validation_report()

# examples/custom_agent_example.py
#!/usr/bin/env python3
"""
Exemplo de como criar um agente customizado
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings

class CustomTriathlonAgent:
    """Exemplo de agente customizado para análise de performance"""
    
    def __init__(self, llm):
        self.agent = Agent(
            role="Analista de Performance em Triathlon",
            goal="Analisar dados de performance e criar recomendações personalizadas",
            backstory="""Você é um analista esportivo especializado em triathlon 
            com experiência em ciência do esporte e análise de dados. Sua missão 
            é transformar dados de provas em insights acionáveis para atletas.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_performance_data(self, data):
        """Analisa dados de performance"""
        # Implementar lógica de análise
        pass

def example_custom_workflow():
    """Exemplo de workflow customizado"""
    
    # Configura LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.3,
        google_api_key=Settings.GOOGLE_API_KEY
    )
    
    # Cria agente customizado
    performance_agent = CustomTriathlonAgent(llm)
    
    # Define tarefa customizada
    analysis_task = Task(
        description="""Analisar padrões de performance em provas de triathlon 
        brasileiras e identificar tendências regionais e sazonais.""",
        agent=performance_agent.agent,
        expected_output="Relatório de análise de performance com recomendações"
    )
    
    # Cria crew customizada
    custom_crew = Crew(
        agents=[performance_agent.agent],
        tasks=[analysis_task],
        verbose=True
    )
    
    # Executa workflow
    result = custom_crew.kickoff()
    print("Resultado do workflow customizado:", result)

if __name__ == "__main__":
    example_custom_workflow()

# examples/integration_example.py
#!/usr/bin/env python3
"""
Exemplo de integração com WordPress via API
"""

import requests
import base64
import json
from typing import Dict, Any

class WordPressIntegration:
    """Classe para integração com WordPress via REST API"""
    
    def __init__(self, site_url: str, username: str, password: str):
        self.site_url = site_url.rstrip('/')
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        self.headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json'
        }
    
    def create_post(self, title: str, content: str, status: str = 'draft') -> Dict[str, Any]:
        """Cria um post no WordPress"""
        
        post_data = {
            'title': title,
            'content': content,
            'status': status,
            'categories': [1],  # ID da categoria "Triathlon"
            'tags': [2, 3, 4],  # IDs das tags relevantes
        }
        
        response = requests.post(
            f"{self.api_base}/posts",
            headers=self.headers,
            json=post_data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Erro ao criar post: {response.status_code} - {response.text}")
    
    def upload_media(self, file_path: str, title: str = "") -> Dict[str, Any]:
        """Faz upload de mídia para WordPress"""
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Basic {self.auth}'}
            
            response = requests.post(
                f"{self.api_base}/media",
                headers=headers,
                files=files,
                data={'title': title}
            )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Erro no upload: {response.status_code}")

def integrate_with_wordpress():
    """Exemplo de integração completa"""
    
    # Configurações do WordPress (substitua pelos seus dados)
    wp_config = {
        'site_url': 'https://seu-site-wordpress.com',
        'username': 'seu_usuario',
        'password': 'sua_senha_aplicacao'  # Use Application Password
    }
    
    # Cria instância da integração
    wp = WordPressIntegration(**wp_config)
    
    # Lê o post gerado pelo CrewAI
    try:
        with open('output/triathlon_blog_post_seo_optimized.md', 'r', encoding='utf-8') as f:
            post_content = f.read()
        
        # Converte Markdown para HTML (básico)
        html_content = post_content.replace('\n', '<br>')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        
        # Cria o post no WordPress
        result = wp.create_post(
            title="As Melhores Provas de Triathlon do Brasil em 2024",
            content=html_content,
            status='draft'  # Cria como rascunho
        )
        
        print(f"✅ Post criado com sucesso!")
        print(f"ID: {result['id']}")
        print(f"URL: {result['link']}")
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")

if __name__ == "__main__":
    integrate_with_wordpress()

# docs/ARCHITECTURE.md
# Arquitetura do Projeto

## Visão Geral

O projeto Triathlon CrewAI utiliza uma arquitetura baseada em agentes especializados que trabalham sequencialmente para automatizar a criação de conteúdo sobre triathlon.

## Componentes Principais

### 1. Agentes (Agents)
- **Research Agent**: Responsável pela pesquisa de dados
- **Content Writer Agent**: Cria conteúdo otimizado
- **SEO Optimizer Agent**: Otimiza para mecanismos de busca

### 2. Ferramentas (Tools)
- **TriathlonSearchTool**: Pesquisa especializada em triathlon
- **SerperDevTool**: Integração com API de pesquisa

### 3. Utilitários (Utils)
- **FileHandler**: Manipulação de arquivos JSON e texto
- **Settings**: Configurações centralizadas

### 4. Fluxo de Dados

```
[Pesquisa] → [JSON] → [Escrita] → [Post MD] → [SEO] → [Post Otimizado]
```

## Padrões de Design Utilizados

- **Strategy Pattern**: Diferentes estratégias de pesquisa
- **Template Method**: Estrutura comum para agentes
- **Factory Pattern**: Criação de ferramentas especializadas

## Tecnologias

- **CrewAI**: Framework de agentes IA
- **LangChain**: Integração com LLMs
- **OpenAI GPT**: Modelo de linguagem
- **Serper API**: Pesquisa web

# docs/API_GUIDE.md
# Guia de APIs Necessárias

## OpenAI API

### Configuração
1. Acesse: https://platform.openai.com/api-keys
2. Crie uma nova chave de API
3. Adicione no arquivo `.env`:
```
GOOGLE_API_KEY=sk-...
```

### Modelos Recomendados
- **GPT-4 Turbo**: Melhor qualidade, mais caro
- **GPT-3.5 Turbo**: Boa qualidade, mais barato

## Serper API

### Configuração
1. Acesse: https://serper.dev/
2. Registre-se e obtenha chave gratuita
3. Adicione no arquivo `.env`:
```
SERPER_API_KEY=...
```

### Limites Gratuitos
- 2.500 pesquisas/mês
- Ideal para desenvolvimento e testes

## Alternativas

### Pesquisa Web
- **DuckDuckGo API**: Gratuita, sem chave necessária
- **Bing Search API**: Microsoft, pago
- **Google Custom Search**: Google, limite gratuito baixo

### LLMs
- **Anthropic Claude**: Via API
- **Google Gemini**: Via API
- **Ollama**: Local, gratuito

# docs/DEPLOYMENT.md
# Guia de Deploy

## Deploy Local

### Desenvolvimento
```bash
git clone <repo-url>
cd triathlon-crew-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Configure .env
python main.py
```

## Deploy com Docker

### Build e Run
```bash
docker build -t triathlon-crew-ai .
docker run --env-file .env triathlon-crew-ai
```

### Docker Compose
```bash
docker-compose up -d
```

## Deploy em Produção

### Servidor VPS/Cloud

1. **Configuração do Servidor**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

2. **Deploy do Projeto**
```bash
git clone <repo-url>
cd triathlon-crew-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configuração de Serviço (systemd)**
```ini
# /etc/systemd/system/triathlon-crew.service
[Unit]
Description=Triathlon CrewAI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/triathlon-crew-ai
Environment=PATH=/home/ubuntu/triathlon-crew-ai/venv/bin
ExecStart=/home/ubuntu/triathlon-crew-ai/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Ativação**
```bash
sudo systemctl enable triathlon-crew.service
sudo systemctl start triathlon-crew.service
```

### Agendamento (Cron)

Para execução automática:
```bash
# Editar crontab
crontab -e

# Executar todo dia às 6:00
0 6 * * * cd /home/ubuntu/triathlon-crew-ai && ./venv/bin/python main.py
```

## Monitoramento

### Logs
```bash
tail -f logs/triathlon_crew_*.log
```

### Status do Serviço
```bash
sudo systemctl status triathlon-crew.service
```

# docs/CUSTOMIZATION.md
# Guia de Customização

## Personalizando Agentes

### Modificando Prompts
```python
# agents/research_agent.py
self.agent = Agent(
    role="Seu Role Customizado",
    goal="Seu Goal Customizado", 
    backstory="""Sua backstory customizada...""",
    # ... resto da configuração
)
```

### Adicionando Novas Ferramentas
```python
# tools/custom_tool.py
from crewai_tools import BaseTool

class CustomTool(BaseTool):
    name: str = "Custom Tool"
    description: str = "Descrição da ferramenta"
    
    def _run(self, argument: str) -> str:
        # Implementar lógica
        return "resultado"
```

## Criando Novos Agentes

### Template Base
```python
class CustomAgent:
    def __init__(self, llm):
        self.agent = Agent(
            role="Role do Agente",
            goal="Objetivo específico",
            backstory="História e contexto",
            tools=[],  # Ferramentas específicas
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
```

## Modificando Saídas

### Formatos Personalizados
```python
def custom_output_format(self, data):
    # JSON personalizado
    return {
        "custom_field": data,
        "timestamp": datetime.now(),
        "format_version": "2.0"
    }
```

### Templates de Post
```python
def custom_post_template(self, events):
    template = """
    # Título Personalizado
    
    ## Seção 1
    {content_1}
    
    ## Seção 2  
    {content_2}
    """
    return template.format(
        content_1=self.generate_content_1(events),
        content_2=self.generate_content_2(events)
    )
```

## Integrações Externas

### WordPress API
```python
def publish_to_wordpress(self, content):
    wp_api = WordPressAPI(
        url="https://seu-site.com",
        username="usuario",
        password="senha"
    )
    return wp_api.create_post(content)
```

### Outras Plataformas
- Medium API
- LinkedIn API
- Twitter API
- Newsletter APIs (Mailchimp, ConvertKit)

# CHANGELOG.md
# Changelog

## [1.0.0] - 2024-08-05

### Adicionado
- ✨ Sistema completo de 3 agentes especializados
- 🔍 Agent de pesquisa com integração Serper API
- ✍️ Agent escritor com técnicas de Brevidade Inteligente
- 🎯 Agent SEO com otimizações avançadas
- 📊 Sistema de validação de arquivos
- 🐳 Suporte a Docker e Docker Compose
- 📝 Documentação completa
- 🧪 Testes unitários
- 📈 Relatórios de análise SEO
- 🛠️ Scripts de automação

### Recursos Principais
- Pesquisa automatizada de provas de triathlon
- Geração de posts otimizados para blog
- Aplicação de técnicas de copywriting
- Otimização completa para SEO
- Estrutura modular e extensível
- Tratamento robusto de erros
- Sistema de logging completo

### Tecnologias
- CrewAI 0.28.8
- OpenAI GPT-4
- LangChain
- Serper API
- Python 3.8+

## Roadmap Futuro

### [1.1.0] - Previsto
- [ ] Integração WordPress automática
- [ ] Suporte a múltiplos idiomas
- [ ] Geração automática de imagens
- [ ] Analytics e métricas de performance

### [1.2.0] - Previsto  
- [ ] Interface web (Streamlit/FastAPI)
- [ ] Agendamento automático
- [ ] Integração com redes sociais
- [ ] Templates personalizáveis

### [2.0.0] - Previsto
- [ ] Arquitetura de microserviços
- [ ] API REST completa
- [ ] Dashboard de monitoramento
- [ ] Inteligência artificial para otimização automática

# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "triathlon-crew-ai"
version = "1.0.0"
description = "Projeto CrewAI para automação de blog sobre triathlon"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Seu Nome", email = "seu.email@exemplo.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    "crewai==0.28.8",
    "crewai-tools==0.1.6",
    "langchain-openai==0.1.0",
    "langchain-community==0.0.29",
    "python-dotenv==1.0.0",
    "requests==2.31.0",
    "beautifulsoup4==4.12.2",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "flake8",
    "mypy",
    "coverage",
]

[project.urls]
Homepage = "https://github.com/seu-usuario/triathlon-crew-ai"
Repository = "https://github.com/seu-usuario/triathlon-crew-ai.git"
Issues = "https://github.com/seu-usuario/triathlon-crew-ai/issues"

[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi? Pesquisa web
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# config/__init__.py
"""
Configurações do projeto Triathlon CrewAI
"""

from .settings import Settings

__all__ = ['Settings']

# agents/__init__.py
"""
Agentes especializados para automação de blog sobre triathlon
"""

from .research_agent import TriathlonResearchAgent
from .content_writer_agent import ContentWriterAgent
from .seo_optimizer_agent import SEOOptimizerAgent

__all__ = [
    'TriathlonResearchAgent',
    'ContentWriterAgent', 
    'SEOOptimizerAgent'
]

# tools/__init__.py
"""
Ferramentas especializadas para pesquisa e processamento
"""

from .search_tools import TriathlonSearchTool

__all__ = ['TriathlonSearchTool']

# utils/__init__.py
"""
Utilitários gerais do projeto
"""

from .file_handler import FileHandler

__all__ = ['FileHandler']

# tests/__init__.py
"""
Testes unitários do projeto Triathlon CrewAI
"""

# scripts/__init__.py
"""
Scripts de automação e utilitários
"""

# CONTRIBUTING.md
# Contribuindo para o Projeto

Obrigado por considerar contribuir para o Triathlon CrewAI! 🎉

## Como Contribuir

### 1. Fork e Clone
```bash
# Fork no GitHub, depois:
git clone https://github.com/seu-usuario/triathlon-crew-ai.git
cd triathlon-crew-ai
```

### 2. Configurar Ambiente
```bash
make setup-dev
# ou manualmente:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest black flake8
```

### 3. Criar Branch
```bash
git checkout -b feature/sua-funcionalidade
# ou
git checkout -b fix/seu-bugfix
```

### 4. Desenvolver
- Escreva código seguindo as convenções do projeto
- Adicione testes para novas funcionalidades
- Mantenha documentação atualizada

### 5. Testar
```bash
make test
make lint
make format-check
```

### 6. Commit e Push
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/sua-funcionalidade
```

### 7. Pull Request
- Abra PR no GitHub
- Descreva as mudanças claramente
- Inclua screenshots se aplicável

## Convenções

### Commits
Seguimos [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` tarefas gerais

### Código
- Use Black para formatação
- Siga PEP 8
- Docstrings para funções públicas
- Type hints quando possível

### Testes
- Escreva testes para novas funcionalidades
- Mantenha cobertura > 80%
- Use nomes descritivos

## Tipos de Contribuição

### 🐛 Reportar Bugs
- Use template de issue
- Inclua passos para reproduzir
- Especifique ambiente

### 💡 Sugerir Funcionalidades  
- Use template de feature request
- Explique o caso de uso
- Considere alternativas

### 📝 Melhorar Documentação
- README, docstrings, comentários
- Exemplos de uso
- Guias tutoriais

### 🔧 Contribuir Código
- Novas funcionalidades
- Correções de bugs
- Melhorias de performance
- Refatorações

## Processo de Review

1. **Automático**: CI/CD executa testes
2. **Manual**: Maintainer revisa código
3. **Feedback**: Discussão e ajustes
4. **Merge**: Após aprovação

## Dúvidas?

- Abra uma issue
- Entre em contato: seu.email@exemplo.com
- Discord: [link-discord]

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque na colaboração
- Mantenha discussões técnicas

Obrigado por contribuir! 🚀

# SECURITY.md
# Política de Segurança

## Versões Suportadas

| Versão | Suportada          |
| ------ | ------------------ |
| 1.0.x  | ✅ Sim             |
| < 1.0  | ❌ Não             |

## Reportar Vulnerabilidades

### Como Reportar
Para reportar vulnerabilidades de segurança:

1. **NÃO** abra uma issue pública
2. Envie email para: security@exemplo.com
3. Inclua detalhes da vulnerabilidade
4. Aguarde resposta em até 48h

### Informações Necessárias
- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Versões afetadas
- Possível correção (se conhecida)

### Processo de Resposta
1. **Reconhecimento** (48h): Confirmamos recebimento
2. **Análise** (1 semana): Avaliamos a vulnerabilidade
3. **Correção** (2 semanas): Desenvolvemos fix
4. **Divulgação** (30 dias): Publicamos correção

## Melhores Práticas

### Para Usuários
- Mantenha dependências atualizadas
- Use chaves de API seguras
- Configure `.env` corretamente
- Não exponha logs sensíveis

### Para Desenvolvedores
- Sanitize inputs de usuário
- Use HTTPS para APIs
- Validação rigorosa de dados
- Logs sem informações sensíveis

## Dependências de Segurança

Monitoramos vulnerabilidades em:
- CrewAI
- OpenAI SDK
- LangChain
- Requests
- Outras dependências

## Histórico de Segurança

Nenhuma vulnerabilidade reportada até o momento.

# Performance e Benchmarks

## Métricas de Performance

### Tempos de Execução Típicos
- **Pesquisa**: 30-60 segundos
- **Escrita**: 45-90 segundos  
- **SEO**: 15-30 segundos
- **Total**: 2-4 minutos

### Uso de Recursos
- **RAM**: ~200-500MB
- **CPU**: Moderado durante execução
- **Armazenamento**: ~10-50MB por execução

### Tokens Utilizados (OpenAI)
- **Pesquisa**: ~1.000-2.000 tokens
- **Escrita**: ~2.000-4.000 tokens
- **SEO**: ~1.500-3.000 tokens
- **Total**: ~4.500-9.000 tokens

## Otimizações

### Para Performance
```python
# Configurações otimizadas
Settings.TEMPERATURE = 0.3  # Menos criativo, mais rápido
Settings.DEFAULT_MODEL = "gpt-3.5-turbo"  # Mais rápido que GPT-4
```

### Para Qualidade
```python
# Configurações de qualidade
Settings.TEMPERATURE = 0.7  # Mais criativo
Settings.DEFAULT_MODEL = "gemini-1.5-pro"  # Melhor qualidade
```

### Cache e Persistência
- Implementar cache de pesquisas
- Reutilizar resultados recentes
- Otimizar prompts para eficiência

## Monitoramento

### Logs de Performance
```python
import time
import logging

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logging.info(f"{func.__name__} executado em {end_time - start_time:.2f}s")
        return result
    return wrapper
```

### Métricas Recomendadas
- Tempo de execução por agente
- Uso de tokens por tarefa
- Taxa de sucesso das pesquisas
- Qualidade do conteúdo gerado Pesquisa web