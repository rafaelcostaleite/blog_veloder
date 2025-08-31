import os
import json
import yaml
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools import SerperSearchTool, PostWriterTool, DesignTool, SEOTool

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
    Retorne os dados JSON completos da pesquisa para que o próximo agente possa processar.
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
    Crie um post completo em formato Markdown sobre: {subject}
    
    1. Analise os dados JSON de pesquisa recebidos do agente pesquisador
    2. Escreva um artigo estruturado em Markdown com:
       - Título atrativo (# Título)
       - Introdução
       - Seções com subtítulos (## Subtítulo, ### Subsubtítulo)
       - Conclusão
       - Lista de fontes quando apropriado
    3. Retorne o conteúdo completo em Markdown para o próximo agente (Designer)
    
    O post deve ser informativo, bem estruturado e em formato Markdown válido.
    """
    
    return Task(
        description=task_description,
        expected_output=config.get('expected_output', 'Conteúdo em Markdown completo'),
        agent=agent
    )

def create_design_agent(llm):
    return Agent(
        role="Designer Web",
        goal="Converter conteúdo markdown em HTML responsivo e mobile-first usando templates",
        backstory="Você é um designer web especialista em criar layouts responsivos e experiências mobile-first. Você domina HTML, CSS e princípios de design responsivo.",
        llm=llm,
        verbose=True
    )

def create_seo_agent(llm):
    return Agent(
        role="Especialista SEO",
        goal="Otimizar HTML para mecanismos de busca aplicando as melhores práticas de SEO",
        backstory="Você é um especialista em SEO com anos de experiência em otimização de sites. Você conhece todas as melhores práticas de SEO técnico, semântico e estrutural.",
        llm=llm,
        verbose=True
    )

def create_design_task(agent, subject):
    task_description = f"""
    Converta o conteúdo markdown recebido do agente jornalista em HTML responsivo sobre: {subject}
    
    1. Analise o conteúdo markdown recebido
    2. Use a ferramenta Design Tool para converter para HTML responsivo
    3. Aplique o template localizado em data/input/template/template.html
    4. Garanta que o design seja mobile-first e responsivo
    5. Retorne o HTML completo para o próximo agente (SEO)
    
    O HTML deve ser bem estruturado, acessível e otimizado para dispositivos móveis.
    """
    
    return Task(
        description=task_description,
        expected_output="HTML responsivo bem estruturado",
        agent=agent,
        tools=[DesignTool()]
    )

def create_seo_task(agent, subject):
    task_description = f"""
    Otimize o HTML recebido do agente de design para SEO sobre: {subject}
    
    1. Analise o HTML recebido do agente de design
    2. Aplique as melhores práticas de SEO:
       - Meta tags otimizadas
       - Estrutura de dados (JSON-LD)
       - Otimização de headings
       - URLs canônicas
       - Meta robots
       - Alt text em imagens
    3. Use a ferramenta SEO Tool para aplicar as otimizações
    4. Salve o HTML final otimizado na pasta data/output/post/
    
    O HTML deve estar completamente otimizado para mecanismos de busca.
    """
    
    return Task(
        description=task_description,
        expected_output="HTML otimizado para SEO salvo com sucesso",
        agent=agent,
        tools=[SEOTool()]
    )