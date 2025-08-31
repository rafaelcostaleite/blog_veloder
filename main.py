#!/usr/bin/env python3
import os
import yaml
from dotenv import load_dotenv
from crewai import Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents import create_research_agent, create_journalist_agent, create_design_agent, create_seo_agent, create_research_task, create_writing_task, create_design_task, create_seo_task

def load_config():
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_subject():
    subject_file = "data/input/subject/topic.txt"
    if os.path.exists(subject_file):
        with open(subject_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return "Inteligência Artificial"

def main():
    load_dotenv()
    
    config = load_config()
    subject = load_subject()
    
    print(f"🚀 Iniciando projeto Blog Veloder...")
    print(f"📝 Tema da pesquisa: {subject}")
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ GOOGLE_API_KEY não encontrada no arquivo .env")
        return
    
    serper_api_key = os.getenv('SERPER_API_KEY')
    if not serper_api_key:
        print("❌ SERPER_API_KEY não encontrada no arquivo .env")
        return
    
    llm = ChatGoogleGenerativeAI(
        model=config['agents']['model'],
        temperature=config['agents']['temperature'],
        google_api_key=google_api_key
    )
    
    researcher = create_research_agent(llm)
    journalist = create_journalist_agent(llm)
    designer = create_design_agent(llm)
    seo_expert = create_seo_agent(llm)
    
    research_task = create_research_task(researcher, subject)
    writing_task = create_writing_task(journalist, subject)
    design_task = create_design_task(designer, subject)
    seo_task = create_seo_task(seo_expert, subject)
    
    crew = Crew(
        agents=[researcher, journalist, designer, seo_expert],
        tasks=[research_task, writing_task, design_task, seo_task],
        verbose=config['agents']['verbose']
    )
    
    print("🔍 Executando pipeline completo...")
    print("📝 Fluxo: Pesquisador → Jornalista → Designer → SEO Expert")
    try:
        result = crew.kickoff()
        
        print("✅ Pipeline concluído!")
        print(f"📄 Resultado final: {result}")
        
        print("🎉 Post HTML otimizado salvo em /data/output/post/!")
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()