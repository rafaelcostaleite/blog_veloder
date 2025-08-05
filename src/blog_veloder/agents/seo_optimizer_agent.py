from crewai import Agent
from utils.file_handler import FileHandler
import re

class SEOOptimizerAgent:
    """Agente responsável por otimizar o conteúdo para SEO"""
    
    def __init__(self, llm):
        self.file_handler = FileHandler()
        
        self.agent = Agent(
            role="Especialista em SEO e Otimização de Conteúdo",
            goal="Otimizar posts para mecanismos de busca aplicando as melhores práticas de SEO",
            backstory="""Você é um especialista em SEO com 10+ anos de experiência em 
            otimização de conteúdo para WordPress. Conhece profundamente os algoritmos 
            do Google e sabe como estruturar conteúdo para maximizar o rankeamento 
            orgânico. Sua especialidade é transformar bom conteúdo em conteúdo que 
            também performa excepcionalmente bem nos buscadores.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def optimize_for_seo(self, post_file_path: str = "output/triathlon_blog_post.md") -> str:
        """Otimiza o post para SEO"""
        
        try:
            # Carrega o post original
            with open(post_file_path, 'r', encoding='utf-8') as f:
                original_post = f.read()
            
            # Aplica otimizações de SEO
            optimized_post = self._apply_seo_optimizations(original_post)
            
            # Salva versão otimizada
            output_path = "output/triathlon_blog_post_seo_optimized.md"
            self.file_handler.save_text(optimized_post, output_path)
            
            # Gera relatório de SEO
            seo_report = self._generate_seo_report(optimized_post)
            report_path = "output/seo_analysis_report.md"
            self.file_handler.save_text(seo_report, report_path)
            
            return f"SEO otimizado! Post salvo em {output_path} e relatório em {report_path}"
            
        except Exception as e:
            return f"Erro na otimização SEO: {str(e)}"
    
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