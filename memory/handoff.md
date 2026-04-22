---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-04-21 (Memory curator + session-open)

**Read before acting:**

- `AGENTS.md`, `memory/MEMORY.md`, `PENDING_LOG.md`, `ERROR_LOG.md`

**Current state:**

- Branch `main`, HEAD a5dce5d (merge PR #31 from feat/007-baseline-green)
- 308/308 testes, 92% cobertura, ruff clean, sem drift de origin
- Três features prontas para ação: `llm-wiki-v2-foundation` (PLAN_READY), `ingest-url` (WORKFLOW_OK), `006-kb-archive` (WORKFLOW_OK)
- `kb/audit.py` + testes sem feature associada — decisão pendente
- Memória distribuída atualizada nesta sessão

**Open points:**

- Escolher frente principal: llm-wiki-v2-foundation (maior impacto) ou ingest-url/006-kb-archive (commit rápido)
- Decidir destino de `kb/audit.py` (feature nova, absorver, ou descartar)
- Limpar features órfãs (`001-wikilink-traversal/` e concluídas sem .state)

**Recommended next front:**

> Comece pela frente de maior impacto: `llm-wiki-v2-foundation` está em PLAN_READY. Crie branch `feat/008-llm-wiki-v2-foundation` (verifique numeração em `features/`), rode `test-red` para gerar testes RED a partir da SPEC/PLAN/TASKS, e avance para `green-refactor`. Se preferir algo rápido primeiro, commit `ingest-url` e `006-kb-archive` via `git-flow-manager` (ambas WORKFLOW_OK).
