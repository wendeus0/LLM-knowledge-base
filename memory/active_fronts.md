---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frente ativa

### Plano de robustez do core (2026-07-09)

**Status:** em execução — plano em `docs/superpowers/plans/2026-07-09-core-robustness.md`
**Branches:** uma por fase (chore/truth-sync → ci/test-gate → fix/pipeline-hardening → feat/article-template → refactor/dead-code-cut → test/uncovered-modules → feat/008 → feat/009 → feat/010-spec), empilhadas até merge
**Resumo:** review completo (4 lentes) → hardening do pipeline ingest→compile→qa→heal, template de artigo como artefato core (engine + override por vault), cortes de código morto, CI com pytest+ruff, cobertura de módulos nus, backlog 008/009 e SPEC de 010.

---

## Frentes em backlog (SPEC draft)

### 008-kb-stats — comando `kb stats` (dashboard Rich). Primitivas em `kb/analytics/` e `kb/claims.py`. ~3h.
### 009-kb-diff — comando `kb diff` (git diff da wiki com Rich). Wrap de git, zero deps novas. ~2h.
### 010-multi-vault-foundation — **meta real, SPEC pendente** (decisão do dono 2026-07-09). Task 13 do plano produz o draft; HITL do dono antes de avançar. Pré-requisito citado: `kb/config.py` resolve paths no import.

---

## Frentes concluídas

- **llm-wiki-v2-foundation** — mergeada via PR #35 (`4835419`); artefatos em `features/_archived/`.
- **ingest-url** — mergeada via PR #32 (`6072c1d`).
- **006-kb-archive** — mergeada via PR #31 + arquivamento via PR #33; diretório movido para `features/_archived/` em 2026-07-09.

---

## Decisões abertas

Ver "Open questions" no plano (`docs/superpowers/plans/2026-07-09-core-robustness.md`): bump de versão 0.5.0, conteúdo fino do template de artigo, quarentena vs skip no heal.

## Decisões resolvidas nesta rodada (2026-07-09)

- Multi-vault é meta real sem SPEC (não drift de doc) → Task 13 do plano.
- Cortar todo código morto (runner.py, savings, wrappers cmds/lint|search).
- Backlog 008/009 entra como fase final do plano.
- Template de artigo: default versionado na engine (`kb/templates/`) com override em `<KB_DATA_DIR>/templates/`.
