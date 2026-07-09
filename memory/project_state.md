---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estado global

Atualizada: 2026-07-09

- **Branch:** `chore/truth-sync` (Fase 0 do plano de robustez; main @ a12ef49)
- **Tests:** `327 passed, 0 failed` ✅ (fix do teste bomba-relógio de analytics/history em 2026-07-09)
- **Lint:** ruff `kb tests` clean
- **Python:** 3.11+ (venv local Python 3.14, `.venv/`)
- **CI:** workflows atuais só rodam gates operacionais (`jobs gate`, `doc-gate`); pytest+ruff entram na Fase 1 do plano

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
├── tests/            ← 327 testes (unit + integration)
├── docs/adr/         ← ADRs 0001–0016
├── docs/superpowers/plans/ ← plano de robustez 2026-07-09
├── features/         ← 008/009 (SPEC draft); concluídas em _archived/
├── pyproject.toml
└── memory/           ← memória distribuída (este diretório)

<KB_DATA_DIR>/
├── raw/              ← documentos fonte + books/
├── wiki/             ← markdown compilado
├── outputs/          ← file-backs de QA
└── kb_state/         ← manifesto + stores knowledge/learnings
```

## ADRs

0001–0016. Destaques: ADR-0015 (runtime topic taxonomy), ADR-0016 (--commit explícito).

## Marcos (Milestones)

1–10 concluídos (baseline, livros, Pal, execução sensível, expansão funcional, validação real, qualidade de output, compile paralelo, cobertura, baseline green + SSRF).
11. **LLM Wiki v2 Foundation** ✅ (PR #35)
12. **Robustez do core + template de artigo** ← em execução (plano 2026-07-09)
