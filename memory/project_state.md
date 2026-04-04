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
│   ├── cybersecurity/, ai/, python/, typescript/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, book_import.py, book_import_core.py
│   ├── qa.py, search.py, heal.py, lint.py, git.py, cli.py, config.py
├── tests/            ← suíte unit + integration
├── docs/adr/         ← ADRs arquiteturais
├── SECURITY_AUDIT_REPORT.md
├── pyproject.toml
├── .env.example
├── CLAUDE.md, AGENTS.md, ERROR_LOG.md, PENDING_LOG.md
├── memory/           ← memória distribuída
└── .git/             ← versionado
```

## Status

**Iniciativa:** Sprint de integração book-import + endurecimento operacional
- ✓ `kb` consolidado como implementação principal para importação de livros
- ✓ `kb import-book` integrado ao produto
- ✓ `kb import-book --compile` compila capítulos importados para `wiki/`
- ✓ `kb compile` varre `raw/` recursivamente, incluindo `raw/books/`
- ✓ Regras de compatibilidade OpenCode Go adicionadas (`kimi-k2.5`, `minimax-2.7`, `glm-5`)
- ✓ OpenAI SDK movido para extra opcional `.[llm]`
- ✓ Suite `kb`: 53 testes passando
- ✓ Suite `book2md`: 17 testes passando
- ✓ Ruff limpo em ambos os repositórios

## Branches

`main` — projeto solo, sem branches de feature no momento

## Marcos

Sprint fechado em 2026-04-03

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

3. **Validação operacional real** (próximo)
   - [ ] Smoke test com OpenCode Go real
   - [ ] Política para conteúdo sensível + commits automáticos
   - [ ] Refinar distribuição entre `book2md` e `kb`

## Tecnologias

- **Language:** Python 3.11+
- **CLI:** Typer
- **UI:** Rich
- **LLM client:** OpenAI SDK opcional (provider OpenAI-compatible)
- **Provider default:** OpenCode Go
- **Search:** contagem simples de palavras-chave em Markdown
- **Storage:** Markdown, JSON, Git
