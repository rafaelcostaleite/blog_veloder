import os
import json
import yaml
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools import SerperSearchTool, PostWriterTool, save_search_results

def load_agent_config(agent_name):
    with open(f"src/agents/{agent_name}.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    config = {}
    lines = content.strip().split('\n')
    current_key = None
    current_value = []
    
    for line in lines:
        if ':' in line and not line.startswith(' '):
            if current_key:
                config[current_key] = '\n'.join(current_value).strip()
                current_value = []
            current_key, value = line.split(':', 1)
            current_key = current_key.strip()
            if value.strip():
                current_value.append(value.strip())
        else:
            current_value.append(line.strip())
    
    if current_key:
        config[current_key] = '\n'.join(current_value).strip()
    
    return config

def load_task_config(task_name):
    with open(f"src/tasks/{task_name}.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    config = {}
    lines = content.strip().split('\n')
    current_key = None
    current_value = []
    
    for line in lines:
        if ':' in line and not line.startswith(' '):
            if current_key:
                config[current_key] = '\n'.join(current_value).strip()
                current_value = []
            current_key, value = line.split(':', 1)
            current_key = current_key.strip()
            if value.strip():
                current_value.append(value.strip())
        else:
            current_value.append(line.strip())
    
    if current_key:
        config[current_key] = '\n'.join(current_value).strip()
    
    return config

def create_research_agent(llm):
    config = load_agent_config("researcher")
    return Agent(
        role=config.get('role', 'Pesquisador'),
        goal=config.get('goal', 'Pesquisar informações'),
        backstory=config.get('backstory', 'Pesquisador experiente'),
        llm=llm,
        verbose=True
    )

def create_journalist_agent(llm):
    config = load_agent_config("journalist")
    return Agent(
        role=config.get('role', 'Jornalista'),
        goal=config.get('goal', 'Criar conteúdo'),
        backstory=config.get('backstory', 'Jornalista experiente'),
        llm=llm,
        verbose=True
    )

def create_research_task(agent, subject):
    config = load_task_config("research_task")
    
    task_description = f"""
    Realize uma pesquisa abrangente sobre: {subject}
    
    Use a ferramenta SERPER para buscar informações atualizadas.
    Salve os resultados em formato JSON na pasta data/input/search/.
    
    Retorne um resumo das informações encontradas.
    """
    
    return Task(
        description=task_description,
        expected_output=config.get('expected_output', 'Resultados da pesquisa em JSON'),
        agent=agent,
        tools=[SerperSearchTool(os.getenv('SERPER_API_KEY'))]
    )

def create_writing_task(agent, subject):
    config = load_task_config("writing_task")
    
    task_description = f"""
    Crie um post completo em HTML para WordPress sobre: {subject}
    
    1. Leia os arquivos JSON da pasta data/input/search/ que contêm os resultados da pesquisa
    2. Analise as informações coletadas
    3. Escreva um artigo estruturado com:
       - Título atrativo (H1)
       - Introdução
       - Seções com subtítulos (H2, H3)
       - Conclusão
       - Lista de fontes quando apropriado
    4. Use a ferramenta Post Writer para salvar o HTML final na pasta data/output/post/
    
    O post deve ser informativo, bem estruturado e otimizado para WordPress.
    """
    
    return Task(
        description=task_description,
        expected_output=config.get('expected_output', 'Post HTML salvo com sucesso'),
        agent=agent,
        tools=[PostWriterTool()]
    )