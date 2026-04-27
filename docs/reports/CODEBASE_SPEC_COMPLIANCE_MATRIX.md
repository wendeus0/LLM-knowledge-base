# CODEBASE_SPEC_COMPLIANCE_MATRIX.md

Matriz de conformidade SPEC-first/TDD-first por lote de auditoria.

## Legenda de status

- `OK`: módulo com SPEC(s) aplicáveis + testes + ADR (quando decisão durável)
- `PARCIAL`: há lastro, mas falta detalhamento/fechamento documental
- `GAP_SPEC`: comportamento implementado sem SPEC funcional explícita suficiente
- `GAP_ADR`: decisão arquitetural durável sem ADR explícita

---

## Iteração 1 — compile + qa (já executada)

| Módulo | SPEC vinculada | Testes relacionados | Status |
|---|---|---|---|
| `kb/compile.py` | `features/compile-parallel-safe/SPEC.md` | `tests/unit/test_compile_cmds.py`, `tests/unit/test_compile.py` | `OK` |
| `kb/cmds/compile/run.py` | `features/compile-parallel-safe/SPEC.md` | `tests/unit/test_compile_cmds.py`, `tests/unit/test_compile.py` | `OK` |
| `kb/qa.py` | `features/pal-foundation-phase-1/SPEC.md` | `tests/unit/test_qa_cmds.py`, `tests/unit/test_router.py`, `tests/unit/test_qa.py` | `OK` |
| `kb/cmds/qa/run.py` | `features/pal-foundation-phase-1/SPEC.md` | `tests/unit/test_qa_cmds.py`, `tests/unit/test_qa.py` | `OK` |
| `kb/router.py` | `features/pal-foundation-phase-1/SPEC.md`, `features/wikilink-traversal/SPEC.md` | `tests/unit/test_qa_cmds.py`, `tests/unit/test_router.py`, `tests/unit/test_qa.py` | `OK` |
| `kb/client.py` | `features/pal-foundation-phase-1/SPEC.md` | `tests/unit/test_client.py` | `PARCIAL` |
| `kb/state.py` | `features/pal-foundation-phase-1/SPEC.md` | `tests/unit/test_state.py` | `OK` |

---

## Iteração 2 — heal + lint + search + infra

### Domínio heal/lint/search

| Módulo | SPEC(s) principal(is) | ADR(s) | Testes principais | Status | Observação |
|---|---|---|---|---|---|
| `kb/heal.py` | `features/sensitive-execution-controls/SPEC.md`, `features/pal-foundation-phase-1/SPEC.md` | `docs/adr/0005-stochastic-heal-strategy.md`, `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md` | `tests/unit/test_heal.py`, `tests/integration/test_heal_workflow.py`, `tests/unit/test_sensitive_execution_controls.py` | `OK` | Contrato funcional e controles operacionais cobertos |
| `kb/lint.py` | `features/lint-report-contract/SPEC.md`, `features/pal-foundation-phase-1/SPEC.md`, `features/sensitive-execution-controls/SPEC.md` | `docs/adr/0006-pal-inspired-routing-memory-and-guardrails-foundation.md`, `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md` | `tests/unit/test_lint.py`, `tests/unit/test_lint_cmds.py` | `OK` | Contrato de saída formalizado na SPEC dedicada |
| `kb/search.py` | `features/search-keyword-contract/SPEC.md` | `docs/adr/0004-keyword-search-strategy.md` | `tests/unit/test_search.py` | `OK` | GAP_SPEC eliminado com contrato funcional explícito |
| `kb/cmds/search/run.py` | `features/search-keyword-contract/SPEC.md` | `docs/adr/0004-keyword-search-strategy.md` | `tests/unit/test_search.py`, `tests/unit/test_cli.py` | `OK` | Camada de comando vinculada à SPEC dedicada de search |
| `kb/cmds/lint/run.py` | `features/lint-report-contract/SPEC.md`, `features/pal-foundation-phase-1/SPEC.md`, `features/sensitive-execution-controls/SPEC.md` | `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md` | `tests/unit/test_lint_cmds.py` | `OK` | Encaminhamento de flags/execução coberto |

### Domínio infra operacional (CLI/config/git/jobs/client)

| Módulo | SPEC(s) principal(is) | ADR(s) | Testes principais | Status | Observação |
|---|---|---|---|---|---|
| `kb/jobs.py` | `features/jobs-and-git-operational-contract/SPEC.md`, `features/pal-foundation-phase-1/SPEC.md` | `docs/adr/0006-pal-inspired-routing-memory-and-guardrails-foundation.md` | `tests/unit/test_jobs.py`, `tests/unit/test_jobs_registry.py` | `OK` | Contrato de catálogo e execução formalizado |
| `kb/git.py` | `features/jobs-and-git-operational-contract/SPEC.md`, `features/sensitive-execution-controls/SPEC.md`, `features/outputs-store/SPEC.md` | `docs/adr/0003-git-versioning-strategy.md`, `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md` | `tests/unit/test_git.py`, `tests/unit/test_sensitive_execution_controls.py` | `OK` | Contrato operacional consolidado |
| `kb/client.py` | `features/pal-foundation-phase-1/SPEC.md` (parcial), `features/compile-parallel-safe/SPEC.md` (fallback parcial) | `docs/adr/0012-provider-model-compatibility-and-resource-limit-fallback.md` | `tests/unit/test_client.py` | `OK` | GAP_ADR eliminado com ADR dedicada |
| `kb/config.py` | `features/outputs-store/SPEC.md`, `features/wikilink-traversal/SPEC.md` | `docs/adr/0011-externalize-user-corpus-from-engine-repo.md` | `tests/unit/test_outputs.py`, `tests/unit/test_web_ingest.py` | `OK` | Diretórios e parâmetros centrais com lastro documental |
| `kb/cli.py` | `features/cli-surface-contract/SPEC.md`, `features/compile-parallel-safe/SPEC.md`, `features/outputs-store/SPEC.md`, `features/sensitive-execution-controls/SPEC.md`, `features/ingest-url/SPEC.md` | `docs/adr/0002-typer-cli-framework.md` | `tests/unit/test_cli.py`, `tests/unit/test_lint_cmds.py`, `tests/unit/test_compile_cmds.py`, `tests/unit/test_qa_cmds.py` | `OK` | Contrato consolidado de superfície pública em SPEC dedicada |

---

## Consolidação de gaps após execução dos 3 passos

### GAP_SPEC

Nenhum gap aberto no escopo auditado.

### GAP_ADR

Nenhum gap aberto no escopo auditado.

### PARCIAL

Nenhum item parcial no escopo auditado.

---

## Evidências de execução do lote 2 (base)

- Leitura e auditoria documental de SPECs/ADRs do escopo
- Inspeção de código dos módulos auditados
- Execução de testes focados no lote:
  - `python -m pytest tests/unit/test_heal.py tests/unit/test_lint.py tests/unit/test_lint_cmds.py tests/unit/test_search.py tests/unit/test_jobs.py tests/unit/test_cli.py tests/unit/test_git.py tests/unit/test_client.py -q`
  - Resultado: `87 passed in 0.67s`

## Evidências de fechamento dos 3 passos (pós-lote 2)

- Novos artefatos:
  - `features/search-keyword-contract/SPEC.md`
  - `docs/adr/0012-provider-model-compatibility-and-resource-limit-fallback.md`
  - `features/cli-surface-contract/SPEC.md`
  - `features/lint-report-contract/SPEC.md`
  - `features/jobs-and-git-operational-contract/SPEC.md`
- Revalidação de testes:
  - `python -m pytest tests/unit/test_search.py tests/unit/test_client.py tests/unit/test_lint.py tests/unit/test_lint_cmds.py tests/unit/test_jobs.py tests/unit/test_jobs_registry.py tests/unit/test_git.py tests/unit/test_cli.py tests/unit/test_compile_cmds.py tests/unit/test_qa_cmds.py -q`
  - Resultado: `88 passed in 0.51s`
