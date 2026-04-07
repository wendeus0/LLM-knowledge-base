---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Atualizada: 2026-04-07

```text
kb/
├── raw/              ← documentos fonte
│   └── books/        ← livros importados em capítulos markdown + metadata.json
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── summaries/
│   ├── ai/           ← 14 artigos (12 de EPUB "Building Applications with AI Agents")
│   ├── cybersecurity/, python/, typescript/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py, graph.py, outputs.py, web_ingest.py
├── kb_state/         ← manifesto + stores knowledge/learnings
├── tests/            ← suíte unit + integration (113 passando, 8 falhando pré-existentes)
├── docs/adr/         ← ADRs 0001–0007, 0010
├── docs/SENSITIVE_CONTENT_POLICY.md ← política operacional de sensibilidade
├── features/         ← SPECs de implementação
├── pyproject.toml    ← pytest-cov configurado; 80% cobertura baseline
├── memory/           ← memória distribuída
└── .git/             ← branch: main (PR#19 aguardando merge)
```

## Status

**Sprint encerrado:** 2026-04-07 — Validação operacional + qualidade + importação de livro real

- ✅ EPUB "Building Applications with AI Agents" importado → 12 artigos em `wiki/ai/`
- ✅ Smoke test completo: `search`, `lint`, `qa`, `heal`, `import-book --compile` OK com OpenCode Go
- ✅ Política de conteúdo sensível — `docs/SENSITIVE_CONTENT_POLICY.md`
- ✅ pytest-cov instalado; 80% cobertura; HTML em `htmlcov/`
- ✅ ADR-0001 atualizado — A3 (extração de pacote compartilhado) rejeitada formalmente
- ✅ Root cause de code fence wrapping corrigido — SYSTEM prompt + `_strip_outer_fence()`
- ✅ 25 artigos wiki corrompidos por fences restaurados manualmente
- ⏳ PR#19 (feat/wikilink-traversal) aguardando merge

## Branches

`feat/wikilink-traversal` — branch atual; PR#19 aberto aguardando merge para main.

## Marcos (Milestones)

1. **Baseline do produto** ✅
2. **Integração de livros** ✅
3. **Fundação inspirada em Pal** ✅
4. **Controles explícitos de execução sensível** ✅
5. **Expansão funcional** ✅ (outputs store, URL ingest, wikilink traversal, rich book metadata)
6. **Validação operacional real** ✅ (smoke test real, política sensibilidade, cobertura)
7. **Qualidade de output LLM** ✅ (fix code fence, 25 artigos restaurados, ADR-0010 pendente)

## Próximo marco sugerido

8. **Estabilidade de testes** — corrigir 8 falhas pré-existentes em `test_web_ingest.py`
