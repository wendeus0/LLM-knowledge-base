---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Atualizada: 2026-04-08

```text
kb/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py, graph.py, outputs.py, web_ingest.py
├── tests/            ← suíte unit + integration (139 passando)
├── docs/adr/         ← ADRs 0001–0007, 0010
├── docs/SENSITIVE_CONTENT_POLICY.md ← política operacional de sensibilidade
├── features/         ← SPECs de implementação
├── pyproject.toml    ← pytest-cov configurado; 78% cobertura real da suíte completa
├── memory/           ← memória distribuída
└── .git/             ← branch de trabalho: feat/compile-parallel-hardening

<KB_DATA_DIR>/
├── raw/              ← documentos fonte
│   └── books/        ← livros importados em capítulos markdown + metadata.json
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── summaries/
│   ├── ai/           ← 14 artigos (12 de EPUB "Building Applications with AI Agents")
│   ├── cybersecurity/, python/, typescript/
└── kb_state/         ← manifesto + stores knowledge/learnings
```

## Status

**Estado atual:** 2026-04-08 — hardening de compile paralelo seguro + cobertura real da suíte

- ✅ `compile` refatorado para geração pura + persistência serial (`compile_to_artifact`, `persist_artifact`, `compile_many`)
- ✅ `kb compile` suporta `--workers` e `--commit`, com default sem commit
- ✅ `import-book --compile` alinhado ao modelo de batch seguro em paralelo
- ✅ suíte completa verde: `139` testes passando
- ✅ cobertura real da suíte completa: `78%` (`kb/compile.py` 91%, `kb/cli.py` 60%)
- ✅ `features/compile-parallel-safe/SPEC.md` e `REPORT.md` atualizados para handoff e PR

## Branches

`feat/compile-parallel-hardening` — branch atual preparada para commits e PR desta frente.

## Marcos (Milestones)

1. **Baseline do produto** ✅
2. **Integração de livros** ✅
3. **Fundação inspirada em Pal** ✅
4. **Controles explícitos de execução sensível** ✅
5. **Expansão funcional** ✅ (outputs store, URL ingest, wikilink traversal, rich book metadata)
6. **Validação operacional real** ✅ (smoke test real, política sensibilidade, cobertura)
7. **Qualidade de output LLM** ✅ (fix code fence, 25 artigos restaurados, ADR-0010)
8. **Compile paralelo seguro** ✅ (geração paralela, persistência serial, batch seguro para `import-book --compile`)

## Próximo marco sugerido

9. **Cobertura orientada a risco** — subir `kb/cli.py`, `kb/book_import_core.py`, `kb/git.py` e validar concorrência com provider real
