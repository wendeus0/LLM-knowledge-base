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
**Resumo:** Rework da engine de compile com base em SPEC e PLAN aprovados. Próxima etapa é escrever testes RED.

**Escopo absorvido:** `kb/audit.py` + `tests/unit/test_audit.py` (untracked) passam a pertencer a esta feature — entregam RF-07 (trilha de auditoria).

---

## Frentes em backlog (SPEC draft)

### F14: 008-kb-stats

**Status:** SPEC draft
**Esforço:** ~3h
**Artefatos:** `features/008-kb-stats/SPEC.md`
**Resumo:** Comando `kb stats` para dashboard Rich de métricas da wiki. Primitivas já existem em `kb/analytics/` (health, history, gain) e `kb/claims.py`.

### F15: 009-kb-diff

**Status:** SPEC draft
**Esforço:** ~2h
**Artefatos:** `features/009-kb-diff/SPEC.md`
**Resumo:** Comando `kb diff` para visualizar diff de `wiki/` via git com formatação Rich. Wrap de `git diff` — zero dependências novas.

---

## Frentes concluídas nesta rodada

- **F12: ingest-url** — mergeado via PR #32 (commit `6072c1d`) + artefatos docs via PR #32.
- **F13: 006-kb-archive** — mergeado via PR #31 (commit `5f56418`) + arquivamento via PR #33 (commit `6150b4a`).

---

## Decisões abertas

_(nenhuma)_

## Decisões resolvidas nesta rodada

### Q4: O que fazer com kb/audit.py? — **Resolvido (opção B)**

`kb/audit.py` e `tests/unit/test_audit.py` ficam untracked até `llm-wiki-v2-foundation` iniciar; serão commitados na branch da feature como parte de RF-07.

### Q5: Limpar features órfãs? — **Resolvido**

Features concluídas movidas para `features/_archived/`. `001-wikilink-traversal` e demais sem `.state` arquivados.

### Q6: kb diff e kb stats fantasmas em CLAUDE.md — **Resolvido**

`CLAUDE.md:132-133` citava "004-kb-diff" e "005-kb-stats" como entregues, mas não existem no `cli.py`. Corrigido para (backlog) 008/009. SPECs draft criadas em `features/008-kb-stats/` e `features/009-kb-diff/`.
