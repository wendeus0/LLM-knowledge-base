# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

### Adicionado

- `kb ingest <url>`: ingestão de documentos a partir de URL com proteção SSRF (PR #32)
- Fundação da wiki v2: claims lifecycle, discovery, jobs canônicos, analytics e trilha de auditoria (PR #35)
- `kb archive`: move artigos stale/órfãos de `wiki/` para `archive/` com backup versionado (PR #31, #33)
- Suporte ao modelo `kimi-k2.7-code` e roteamento de topic por pasta de origem

### Corrigido

- `kb/audit.py` resolve `AUDIT_PATH` em runtime via `kb.config` (baseline 2026-04-22)
- Teste de `analytics/history` com janela temporal fixa que expirava com o calendário (2026-07-09)

## [0.4.0] - 2026-04-04

### Adicionado

- `README.md` com visão geral do projeto e instruções de uso
- `ARCHITECTURE.md` documentando decisões arquiteturais e estrutura do sistema
- `API.md` com referência da interface de linha de comando
- `CONTRIBUTING.md` com diretrizes de contribuição e políticas de operação
- `ANALYSIS_DOCS.md` com análise de documentação arquitetural

### Corrigido

- Issues de documentação identificados na análise arquitetural

## [0.3.1] - 2026-04-03

### Corrigido

- Baseline D1-D4: correções de documentação, configuração, lint e antipatterns de teste

## [0.3.0] - 2026-04-02

### Adicionado

- Testes unitários para módulos core: `compile`, `qa`, `search`, `heal`, `lint`
- Configuração inicial de testes com pytest
- Reporting checklist e notas de teste

### Corrigido

- 15 issues de testes e documentação
- Adicionado `python-dotenv` às dependências permitidas em D7

## [0.2.0] - 2026-04-01

### Adicionado

- Funcionalidade de importação de livros (`book import`) para EPUB e PDF
- ADR-0001 documentando a decisão arquitetural sobre book import

## [0.1.0] - 2026-03-31

### Adicionado

- Estrutura base do projeto kb
- Sistema de knowledge base pessoal mantido por LLM
- Suporte a ingestão de documentos e compilação para wiki em markdown
- Funcionalidades de Q&A, busca, health checks e healing automático

---

## Legenda

- `Adicionado` — Novas funcionalidades
- `Alterado` — Mudanças em funcionalidades existentes
- `Descontinuado` — Funcionalidades que serão removidas em breve
- `Removido` — Funcionalidades removidas
- `Corrigido` — Correções de bugs
- `Segurança` — Correções de vulnerabilidades de segurança
