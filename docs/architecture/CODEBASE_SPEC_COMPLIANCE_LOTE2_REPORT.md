# CODEBASE_SPEC_COMPLIANCE_LOTE2_REPORT.md

## Data

2026-04-12

## Escopo executado (Lote 2)

- Domínio funcional: `heal`, `lint`, `search`
- Domínio infra operacional: `jobs`, `git`, `client`, `config`, `cli`
- Objetivo: expandir enforcement com classificação formal `GAP_SPEC`, `GAP_ADR`, `PARCIAL`, `OK`

## Método

1. Revisão de SPECs existentes (`features/*/SPEC.md`) no escopo.
2. Revisão de ADRs existentes (`docs/adr/*`) no escopo.
3. Inspeção de implementação real em `kb/*.py` e `kb/cmds/*`.
4. Verificação de cobertura por testes unitários/integrados relacionados.
5. Classificação por módulo com foco em rastreabilidade e risco operacional.

## Evidências executadas

### Comando de validação de testes do lote

`python -m pytest tests/unit/test_heal.py tests/unit/test_lint.py tests/unit/test_lint_cmds.py tests/unit/test_search.py tests/unit/test_jobs.py tests/unit/test_cli.py tests/unit/test_git.py tests/unit/test_client.py -q`

### Resultado

- `87 passed in 0.67s`

## Resultado da auditoria

### Módulos em OK

- `kb/heal.py`
- `kb/cmds/lint/run.py`

### Módulos em PARCIAL

- `kb/config.py` (sem evidência de teste dedicada no comando executado; classificação mantida parcial por rastreabilidade)
- `kb/lint.py` (sem SPEC dedicada para contrato estável de saída)
- `kb/jobs.py` (catálogo ampliado sem SPEC dedicada)
- `kb/git.py` (regras distribuídas em SPECs transversais)
- `kb/cli.py` (superfície pública ampla, sem SPEC consolidada da interface)

### GAP_SPEC (alta prioridade documental)

- `kb/search.py`
- `kb/cmds/search/run.py`

### GAP_ADR

- `kb/client.py` — faltando ADR explícita para:
  - compatibilidade `BASE_URL` x `MODEL`
  - fallback para erro de resource limit do provider

## Avaliação de risco

- Risco alto imediato: `search` sem SPEC (funcionalidade core de descoberta sem contrato formal).
- Risco médio: `client` sem ADR (decisões duráveis já em produção, sem registro decisório dedicado).
- Risco médio/baixo: `lint/jobs/git/cli` em parcial (lastro existe, mas fragmentado).

## Pós-execução dos 3 passos corretivos (2026-04-12)

Após a execução integral dos 3 passos priorizados, os gaps documentais identificados no lote 2 foram fechados no escopo auditado.

### Artefatos criados para fechamento

- `features/search-keyword-contract/SPEC.md`
- `docs/adr/0012-provider-model-compatibility-and-resource-limit-fallback.md`
- `features/cli-surface-contract/SPEC.md`
- `features/lint-report-contract/SPEC.md`
- `features/jobs-and-git-operational-contract/SPEC.md`

### Evidência de regressão

Comando:

`python -m pytest tests/unit/test_search.py tests/unit/test_client.py tests/unit/test_lint.py tests/unit/test_lint_cmds.py tests/unit/test_jobs.py tests/unit/test_jobs_registry.py tests/unit/test_git.py tests/unit/test_cli.py tests/unit/test_compile_cmds.py tests/unit/test_qa_cmds.py -q`

Resultado:

- `88 passed in 0.51s`

## Conclusão

O lote 2 foi concluído e, com os 3 passos corretivos executados em sequência, a matriz de conformidade ficou sem `GAP_SPEC`, sem `GAP_ADR` e sem itens `PARCIAL` no escopo auditado.
