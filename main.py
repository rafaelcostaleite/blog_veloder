#!/usr/bin/env python3
import os
import yaml
from dotenv import load_dotenv
from crewai import Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents import create_research_agent, create_journalist_agent, create_research_task, create_writing_task
from src.post_generator import WordPressPostGenerator

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
    
    research_task = create_research_task(researcher, subject)
    writing_task = create_writing_task(journalist, subject)
    
    crew = Crew(
        agents=[researcher, journalist],
        tasks=[research_task, writing_task],
        verbose=config['agents']['verbose']
    )
    
    print("🔍 Executando pesquisa...")
    try:
        result = crew.kickoff()
        
        print("✅ Processo concluído!")
        print(f"📄 Resultado: {result}")
        
        post_generator = WordPressPostGenerator()
        search_data = post_generator.load_search_data()
        
        if search_data:
            content_pieces, sources = post_generator.extract_content_from_search(search_data)
            
            if content_pieces:
                content = f"""
                <h2>Introdução</h2>
                <p>Este artigo apresenta informações atualizadas sobre {subject}.</p>
                
                <h2>Conteúdo Principal</h2>
                {"".join([f"<div>{piece}</div>" for piece in content_pieces[:5]])}
                
                <h2>Conclusão</h2>
                <p>As informações apresentadas mostram a relevância e atualidade do tema {subject}.</p>
                
                <h3>Fontes</h3>
                <ul>
                {"".join([f"<li><a href='{source}' target='_blank'>{source}</a></li>" for source in sources[:5]])}
                </ul>
                """
                
                html_file = post_generator.generate_html_post(
                    content=content,
                    title=f"Tudo sobre {subject}",
                    meta_description=f"Informações completas e atualizadas sobre {subject}",
                    tags=f"{subject}, blog, informação"
                )
                
                print(f"📝 Post HTML gerado: {html_file}")
            else:
                print("⚠️  Nenhum conteúdo encontrado nos dados de pesquisa")
        else:
            print("⚠️  Nenhum dado de pesquisa encontrado")
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()