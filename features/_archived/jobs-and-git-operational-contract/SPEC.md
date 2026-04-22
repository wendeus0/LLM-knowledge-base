---
title: Jobs and git operational contract
epic: infra
status: approved
pr:
---

# Jobs and git operational contract

## Objetivo

`kb/jobs.py` e `kb/git.py` já suportam catálogo canônico de jobs e commit helper, porém o lastro está fragmentado em múltiplas SPECs; esta feature consolida o contrato operacional para reduzir parcial documental.

## Requisitos funcionais

- [ ] RF-01: catálogo canônico de jobs deve expor ao menos `compile`, `lint`, `review`, `metrics`
- [ ] RF-02: `run_job(<nome>)` deve executar o handler, registrar tracking e retornar saída textual
- [ ] RF-03: nome de job inválido deve falhar com erro explícito listando opções disponíveis
- [ ] RF-04: helper `commit(message, paths, enabled=True)` deve respeitar `enabled=False` sem side effects
- [ ] RF-05: commit helper deve stage por paths relativos, commitar só quando houver mudanças staged e suprimir erro de git indisponível sem quebrar fluxo principal

## Requisitos técnicos

- RT-01: `kb/jobs.py` deve manter separação `JobSpec` vs `JobDefinition`
- RT-02: `kb/git.py` deve manter operação idempotente para ausência de mudanças
- RT-03: testes devem permanecer offline com mock de subprocess e módulos de domínio

## Mudanças de API/CLI

- CLI:
  - `kb jobs list`
  - `kb jobs run <nome>`
- API interna:
  - `list_jobs()`, `run_job(name)`
  - `commit(message, paths, enabled=True)` (assinatura canônica)

## Testes

- Unit:
  - `tests/unit/test_jobs.py` (inclui sucesso + erro explícito para job inválido)
  - `tests/unit/test_jobs_registry.py`
  - `tests/unit/test_git.py`
  - `tests/unit/test_rtk_front.py` (cobre emissão de métricas e leitura de tracking)
- Manual:
  1. `kb jobs list`
  2. `kb jobs run lint`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2h |
| Bloqueador | não |
| Risco | baixo |

## Dependências

- `docs/adr/0003-git-versioning-strategy.md`
- `docs/adr/0006-pal-inspired-routing-memory-and-guardrails-foundation.md`

## ADR

- Necessária? não (já há ADRs de base; esta SPEC consolida contrato operacional)

## Critérios de aceite

- [ ] `kb/jobs.py` e `kb/git.py` deixam de estar em `PARCIAL` por fragmentação documental
- [ ] testes unitários relacionados seguem verdes

## Evidências esperadas

- `python -m pytest tests/unit/test_jobs.py tests/unit/test_jobs_registry.py tests/unit/test_git.py tests/unit/test_rtk_front.py -q`

## Notas

Expansão futura de scheduler persistente/daemon deve abrir nova SPEC específica.
