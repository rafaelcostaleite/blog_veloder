from crewai import Agent
from utils.file_handler import FileHandler
import json

class ContentWriterAgent:
    """Agente responsável por escrever posts otimizados para blog"""
    
    def __init__(self, llm):
        self.file_handler = FileHandler()
        
        self.agent = Agent(
            role="Redator Especialista em Content Marketing",
            goal="Criar posts envolventes e informativos sobre triathlon aplicando técnicas de Brevidade Inteligente",
            backstory="""Você é um redator experiente especializado em content marketing 
            e copywriting esportivo. Domina as técnicas do livro "Brevidade Inteligente" 
            e sabe como criar conteúdo que engaja leitores, mantendo-os interessados do 
            início ao fim. Sua especialidade é transformar dados técnicos em narrativas 
            cativantes e acionáveis.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def write_blog_post(self, json_file_path: str = "data/triathlon_events.json") -> str:
        """Lê o JSON e escreve um post para blog"""
        
        try:
            # Carrega os dados da pesquisa
            triathlon_data = self.file_handler.load_json(json_file_path)
            
            # Cria o post aplicando técnicas de Brevidade Inteligente
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