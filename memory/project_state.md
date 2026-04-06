---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Atualizada: 2026-04-03

```text
kb/
├── raw/              ← documentos fonte
│   └── books/        ← livros importados em capítulos markdown + metadata.json
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── summaries/
│   ├── cybersecurity/, ai/, python/, typescript/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py
├── kb_state/         ← manifesto + stores knowledge/learnings
├── tests/            ← suíte unit + integration
├── docs/adr/         ← ADRs arquiteturais
├── features/         ← SPECs de implementação
├── SECURITY_AUDIT_REPORT.md
├── pyproject.toml
├── .env.example
├── CLAUDE.md, AGENTS.md, ERROR_LOG.md, PENDING_LOG.md
├── memory/           ← memória distribuída
└── .git/             ← versionado
```

## Status

**Sprint atual:** Expansão funcional — outputs store, URL ingest, wikilink traversal, book metadata enriquecida

- ✓ routing por fonte nativa introduzido (`wiki`, `raw`, `knowledge`, `learnings`)
- ✓ stores separados para `knowledge`, `learnings` e `manifest`
- ✓ compile agora gera summary compilado e registra knowledge
- ✓ jobs canônicos `list/run` adicionados
- ✓ guardrails de conteúdo sensível aplicados em runtime
- ✓ flags explícitas `--allow-sensitive` e `--no-commit` adicionadas aos fluxos principais
- ✓ `feat/outputs-store` (PR#12 mergeado): store separado para QA file-back (`kb/outputs.py`)
- ✓ `feat/ingest-url` (PR#13 mergeado): URL scraping via `kb ingest <url>` (`kb/web_ingest.py`)
- ✓ `feat/wikilink-traversal` (PR#14 aberto): QA enriquecido com BFS de wikilinks (`kb/graph.py`)
- ⏳ `feat/rich-book-import-metadata` (PR#15 aberto): metadados EPUB ricos, TOC hierárquico, imagens opcionais
- ✓ fix (2026-04-06): URL-encoded image paths em `book_import_core.py`

## Branches

`main` — PRs #12 e #13 mergeados. PRs #14 (wikilink-traversal) e #15 (rich-book-import-metadata) abertos aguardando merge.

## Marcos (Milestones)

1. **Baseline do produto** (concluído)
   - [x] CLI principal funcionando
   - [x] Git automático em writes da wiki
   - [x] Testes cobrindo módulos principais

2. **Integração de livros** (concluído)
   - [x] Importação EPUB
   - [x] Suporte inicial a PDF textual
   - [x] Compilação recursiva de `raw/books/`
   - [x] Compat layer de `book2md`

3. **Fundação inspirada em Pal** (concluído)
   - [x] Routing por fonte nativa
   - [x] Memória separada (`knowledge` vs `learnings`)
   - [x] Summary compilado + manifesto
   - [x] Jobs canônicos
   - [x] Guardrails/evals automatizadas

4. **Controles explícitos de execução sensível** (concluído)
   - [x] `--allow-sensitive`
   - [x] `--no-commit`
   - [x] documentação operacional inicial

5. **Expansão funcional** (em andamento)
   - [x] outputs store (`kb/outputs.py`)
   - [x] URL ingest (`kb/web_ingest.py`)
   - [x] wikilink traversal (`kb/graph.py`) — PR#14 aguardando merge
   - [x] book metadata enriquecida + TOC hierárquico — PR#15 aguardando merge

6. **Validação operacional real** (em aberto)
   - [ ] Smoke test com OpenCode Go real
   - [ ] Política final para conteúdo sensível
   - [ ] Convenção de uso de `--no-commit`

7. **Avaliação de incrementos** (aguardando subsídios do usuário)
   - [ ] Receber e analisar material externo
   - [ ] Decidir escopo de expansão do produto

## Tecnologias

- **Language:** Python 3.11+
- **CLI:** Typer
- **UI:** Rich
- **LLM client:** OpenAI SDK opcional (provider OpenAI-compatible)
- **Provider default:** OpenCode Go
- **Search:** contagem simples de palavras-chave em Markdown + roteamento por fonte
- **Storage:** Markdown, JSON, Git
