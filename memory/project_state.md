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

**Iniciativa:** Sprint de fundação inspirada em Pal + endurecimento operacional
- ✓ routing por fonte nativa introduzido (`wiki`, `raw`, `knowledge`, `learnings`)
- ✓ stores separados para `knowledge`, `learnings` e `manifest`
- ✓ compile agora gera summary compilado e registra knowledge
- ✓ jobs canônicos `list/run` adicionados
- ✓ guardrails de conteúdo sensível aplicados em runtime
- ✓ flags explícitas `--allow-sensitive` e `--no-commit` adicionadas aos fluxos principais
- ✓ fallback seguro para `defusedxml` e bloqueio de XML inseguro mantidos
- ✓ suíte `kb`: 85 testes passando

## Branches

`feat/readme-arch-docs` — branch atual com mudanças de fundação e endurecimento operacional ainda não commitadas neste fechamento.

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

5. **Validação operacional real** (próximo)
   - [ ] Smoke test com OpenCode Go real
   - [ ] Política final para conteúdo sensível
   - [ ] Convenção de uso de `--no-commit`

## Tecnologias

- **Language:** Python 3.11+
- **CLI:** Typer
- **UI:** Rich
- **LLM client:** OpenAI SDK opcional (provider OpenAI-compatible)
- **Provider default:** OpenCode Go
- **Search:** contagem simples de palavras-chave em Markdown + roteamento por fonte
- **Storage:** Markdown, JSON, Git
