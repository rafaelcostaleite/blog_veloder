# Blog Veloder - Multi-Agent AI System

Sistema avançado de multi-agentes IA para pesquisar informações na internet e gerar posts HTML responsivos e otimizados para SEO.

## Arquitetura

- **Agente Pesquisador**: Busca informações na web usando SERPER API
- **Agente Jornalista**: Transforma dados de pesquisa em conteúdo Markdown estruturado  
- **Agente Designer**: Converte Markdown em HTML responsivo mobile-first usando templates
- **Agente SEO Expert**: Otimiza HTML final aplicando melhores práticas de SEO
- **IA**: Google Gemini 1.5 Flash
- **Orquestração**: CrewAI

## Estrutura do Projeto

```
blog_veloder/
├── data/
│   ├── input/
│   │   ├── subject/topic.txt     # Tema da pesquisa
│   │   └── template/             # Templates HTML responsivos
│   │       └── template.html     # Template base mobile-first
│   └── output/
│       └── post/                 # Posts HTML finais (SEO otimizados)
├── src/
│   ├── agents/                   # Configurações dos agentes
│   ├── tasks/                    # Descrições das tarefas
│   ├── agents.py                 # Criação dos agentes CrewAI
│   └── tools.py                  # Ferramentas (SERPER, Design, SEO)
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

**Pipeline de 4 Agentes Sequenciais:**

1. **🔍 Pesquisador**: Lê tema em `data/input/subject/topic.txt` e busca informações usando SERPER API
   - Retorna dados JSON diretamente para o próximo agente (sem arquivos intermediários)

2. **✍️ Jornalista**: Recebe JSON e cria conteúdo estruturado em Markdown
   - Gera artigo com título, introdução, seções e conclusão
   - Passa conteúdo Markdown para o próximo agente

3. **🎨 Designer**: Converte Markdown em HTML responsivo
   - Utiliza template em `data/input/template/template.html`
   - Aplica design mobile-first e responsivo
   - Gera HTML estruturado

4. **⚡ SEO Expert**: Otimiza HTML final para mecanismos de busca
   - Adiciona meta tags completas
   - Insere JSON-LD structured data
   - Otimiza headings e acessibilidade
   - **Salva resultado final em `data/output/post/`**

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

### Template HTML
- `data/input/template/template.html`: Template responsivo customizável
  - Design mobile-first
  - CSS otimizado para performance
  - Placeholders dinâmicos (`{{TITLE}}`, `{{CONTENT}}`, etc.)
  - Totalmente responsivo (mobile/tablet/desktop)

## Resultado

O sistema gera um arquivo HTML completo e otimizado com:

### ✨ Design & UX
- **HTML responsivo** com design mobile-first
- **CSS otimizado** para performance e carregamento rápido
- **Typography moderna** com fallbacks seguros
- **Layout adaptável** para todos os dispositivos

### 🚀 SEO Avançado  
- **Meta tags completas** (description, keywords, robots)
- **Open Graph** e **Twitter Cards** para redes sociais
- **JSON-LD structured data** para rich snippets
- **Canonical URLs** e meta robots otimizados
- **Alt text automático** em imagens
- **Hierarquia de headings** corrigida (apenas um H1)
- **Tempo de leitura calculado** automaticamente

### 📱 Responsividade
- **Mobile-first approach** com breakpoints otimizados
- **Layout fluido** que se adapta a qualquer tela
- **Typography responsiva** com tamanhos dinâmicos
- **Performance otimizada** para dispositivos móveis

### 📄 Conteúdo
- **Estrutura semântica** com HTML5 adequado
- **Links para fontes** organizados e acessíveis  
- **Formatação profissional** (H1, H2, H3, parágrafos, listas)
- **Metadados automáticos** com data de criação

## 🔧 Regras de Negócio

- ❌ **Arquivos intermediários NÃO são salvos** na pasta `data/`
- ✅ **Dados passam entre agentes via memória** (JSON → Markdown → HTML)  
- ✅ **Apenas o resultado final** é salvo em `/data/output/post/`
- ✅ **Template HTML facilmente customizável** em `/data/input/template/`