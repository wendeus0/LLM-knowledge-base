---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-04-22 (sprint-close + baseline-green)

**Read before acting:**

- `AGENTS.md`, `memory/MEMORY.md`, `PENDING_LOG.md`, `ERROR_LOG.md`
- `memory/active_fronts.md`, `memory/next_steps.md`

**Current state:**

- Branch `fix/baseline-green-2026-04-22`, 3 commits acima de `main @ bc92c60`
- **Baseline:** `311 passed, 0 failed`; cobertura `90%+`
- Ruff `kb/`: clean
- Frente ativa única: `llm-wiki-v2-foundation` (PLAN_READY → test-red)
- Backlog SPEC draft: `008-kb-stats`, `009-kb-diff`
- `kb/audit.py` + `tests/unit/test_audit.py` agora tracked

**O que foi feito nesta sessão:**

1. Diagnóstico das 20 falhas: 18 = `requests` ausente, 2 = AUDIT_PATH fixado no import
2. `pip install -e .[web,dev,llm]` restaurou 18 testes de web_ingest
3. Fix `kb/audit.py`: `from kb.config import AUDIT_PATH` → `import kb.config as _config` (runtime resolution)
4. Commit 1: `fix(audit): resolver AUDIT_PATH via kb.config em runtime`
5. Commit 2: `chore(repo): ignorar htmlcov/ e .pi/tasks/*.json`
6. Commit 3: `chore(docs): sprint-close 2026-04-22` (este commit)
7. Memória e logs atualizados para refletir baseline real

**Open points:**

1. **P1 — `kb/discovery.py` cobertura 25%**: criar `tests/unit/test_discovery.py`
2. **P1 — frente `test-coverage-90`**: branch `feat/test-coverage-90` ainda pendente de push/PR
3. **P2 — higiene**: features mergeadas não movidas para `_archived/`; root MDs órfãs

**Recommended next session:**

> Merge `fix/baseline-green-2026-04-22` em main. Criar branch `feat/llm-wiki-v2-foundation` e iniciar `test-red`. Paralelamente, criar `tests/unit/test_discovery.py` para elevar cobertura de discovery.
