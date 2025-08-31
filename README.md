# Blog Veloder - Multi-Agent AI System

Sistema simplificado de multi-agentes IA para pesquisar informações na internet e gerar posts para WordPress.

## Arquitetura

- **Agente Pesquisador**: Busca informações na web usando SERPER API
- **Agente Jornalista**: Transforma dados de pesquisa em posts HTML para WordPress
- **IA**: Google Gemini 1.5 Flash
- **Orquestração**: CrewAI

## Estrutura do Projeto

```
blog_veloder/
├── data/
│   ├── input/
│   │   ├── subject/topic.txt     # Tema da pesquisa
│   │   └── search/               # Resultados JSON das pesquisas
│   └── output/
│       └── post/                 # Posts HTML gerados
├── src/
│   ├── agents/                   # Configurações dos agentes
│   ├── tasks/                    # Descrições das tarefas
│   ├── agents.py                 # Criação dos agentes CrewAI
│   ├── tools.py                  # Ferramenta SERPER
│   └── post_generator.py         # Gerador de posts HTML
├── config/
│   └── config.yaml              # Configurações gerais
├── .env                         # Variáveis de ambiente
├── docker-compose.yml           # Configuração Docker
├── Dockerfile                   # Imagem Docker
├── requirements.txt             # Dependências Python
└── main.py                      # Script principal
```

## Configuração

1. **Configure as APIs**:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` com suas chaves:
   - `GOOGLE_API_KEY`: Chave da API do Google Gemini
   - `SERPER_API_KEY`: Chave da API do SERPER

2. **Defina o tema de pesquisa**:
   Edite `data/input/subject/topic.txt` com o assunto desejado.

## Execução

### Com Docker (Recomendado)
```bash
docker-compose up --build
```

### Local
```bash
pip install -r requirements.txt
python main.py
```

## Funcionamento

1. **Pesquisa**: O agente pesquisador lê o tema em `data/input/subject/topic.txt` e busca informações usando SERPER
2. **Armazenamento**: Resultados são salvos como JSON em `data/input/search/`
3. **Criação**: O agente jornalista analisa os dados e cria um post HTML
4. **Output**: Post final é salvo em `data/output/post/`

## Configurações

### config/config.yaml
- Modelo de IA (padrão: gemini-1.5-flash)
- Temperatura da geração
- Parâmetros de pesquisa

### Agentes (src/agents/)
- `researcher.txt`: Configuração do pesquisador
- `journalist.txt`: Configuração do jornalista

### Tarefas (src/tasks/)
- `research_task.txt`: Descrição da tarefa de pesquisa
- `writing_task.txt`: Descrição da tarefa de escrita

## Resultado

O sistema gera um arquivo HTML completo com:
- Estrutura otimizada para WordPress
- Meta tags SEO
- Links para fontes
- Formatação adequada (H1, H2, parágrafos, listas)
- Data de criação automática