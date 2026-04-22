---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estado global

Atualizada: 2026-04-22

- **Branch:** `fix/baseline-green-2026-04-22` (3 commits acima de `main @ bc92c60`)
- **Drift:** 0 (baseada em origin/main)
- **Tests:** `311 passed, 0 failed` ✅ (baseline verde)
- **Cobertura:** 90%+ (web_ingest restaura cobertura com `[web]` instalado)
- **Lint:** ruff `kb/` clean
- **Python:** 3.11+ (venv Python 3.14)

> Baseline restaurada nesta sessão. Causas: (1) `pip install -e .[web]` restaurou 18 testes de web_ingest; (2) fix de `kb/audit.py` (runtime AUDIT_PATH) restaurou 3 testes de audit.

## Estrutura do pacote

```text
kb/
├── kb/
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py, book_import_pdf.py
│   ├── graph.py, outputs.py, web_ingest.py, archive.py
│   ├── audit.py, claims.py, doc_gate.py, handoff.py
│   ├── cmds/{compile,qa,lint,search}/run.py
│   ├── core/{runner.py, tracking.py}
│   ├── analytics/{gain.py, health.py, history.py}
│   └── discover/{registry.py, rules.py}
├── tests/            ← 308 testes, 92% cobertura
├── docs/adr/         ← ADRs 0001–0016
├── docs/SENSITIVE_CONTENT_POLICY.md
├── features/         ← SPECs de implementação
├── pyproject.toml
└── memory/           ← memória distribuída (este diretório)

<KB_DATA_DIR>/
├── raw/              ← documentos fonte + books/
├── wiki/             ← markdown compilado
├── outputs/          ← file-backs de QA
└── kb_state/         ← manifesto + stores knowledge/learnings
```

## Snapshot local (afeta próxima sessão)

- Untracked: `features/llm-wiki-v2-foundation/` (.state=PLAN_READY)
- `kb/audit.py` e `tests/unit/test_audit.py` agora tracked (commit f78d903)

## Branches de feature já pushadas

002-search-bm25, 003-kb-watch, 004-kb-diff, 005-kb-stats, 006-kb-archive (WORKFLOW_OK)

## ADRs

0001–0016. Destaques recentes:

- ADR-0015: runtime topic taxonomy
- ADR-0016: explicit commit activation (--commit explícito, --no-commit deprecated)

## Marcos (Milestones)

1. **Baseline do produto** ✅
2. **Integração de livros** ✅
3. **Fundação inspirada em Pal** ✅
4. **Controles explícitos de execução sensível** ✅
5. **Expansão funcional** ✅ (outputs, URL ingest, wikilink, rich book metadata)
6. **Validação operacional real** ✅ (smoke test, política sensibilidade, cobertura)
7. **Qualidade de output LLM** ✅ (fix code fence, ADR-0010)
8. **Compile paralelo seguro** ✅ (geração paralela, persistência serial)
9. **Cobertura orientada a risco** ✅ (308 testes, 92% cobertura)
10. **Baseline green + SSRF protection** ✅ (PR #31 merged, feat/007-baseline-green)

## Próximo marco sugerido

11. **LLM Wiki v2 Foundation** — rework da engine de compile com base em SPEC aprovada
