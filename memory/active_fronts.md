---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F11: llm-wiki-v2-foundation

**Status:** PLAN_READY (próximo: `test-red`)
**Branch:** não criada ainda
**Artefatos:** `features/llm-wiki-v2-foundation/{SPEC.md, PLAN.md, TASKS.md}`
**Resumo:** Rework da engine de compile com base em SPEC aprovada. Próxima etapa é escrever testes RED.

---

### F12: ingest-url

**Status:** WORKFLOW_OK (próximo: `git-flow-manager`)
**Branch:** não criada ainda (código em main como untracked)
**Artefatos:** `features/ingest-url/{PLAN.md, TASKS.md, REPORT.md}`
**Resumo:** Web ingest com proteção SSRF. Pronta para commit/push. Precisa de branch + PR.

---

### F13: 006-kb-archive

**Status:** WORKFLOW_OK (próximo: `git-flow-manager`)
**Branch:** pushada como `feat/006-kb-archive`
**Artefatos:** `features/006-kb-archive/`
**Resumo:** Comando `kb archive` para arquivar documentos. Pronta para commit/push.

---

## Itens sem feature formal

- `kb/audit.py` + `tests/unit/test_audit.py` — módulo de audit implementado mas sem feature SPEC. Decisão pendente: integrar em feature existente, criar feature nova, ou descartar.
- `features/001-wikilink-traversal/` — diretório órfão sem `.state`. Limpar ou arquivar.

---

## Decisões abertas

### Q4: O que fazer com kb/audit.py?

Módulo funcional mas sem SPEC. Opções: (A) criar feature 008-audit, (B) absorver em llm-wiki-v2-foundation, (C) descartar.

### Q5: Limpar features órfãs?

`features/001-wikilink-traversal/` sem .state e múltiplos diretórios de features concluídas sem .state (`cli-surface-contract`, `compile-parallel-safe`, `explicit-commit-contract`, etc.). Decisão: arquivar ou deletar.
