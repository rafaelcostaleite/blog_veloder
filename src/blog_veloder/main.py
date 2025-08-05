from crewai import Crew, Task
from langchain_openai import ChatOpenAI
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
        llm = ChatOpenAI(
            model=Settings.DEFAULT_MODEL,
            temperature=Settings.TEMPERATURE,
            api_key=Settings.OPENAI_API_KEY
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