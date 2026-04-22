---
title: Safe parallel compile report
feature: compile-parallel-safe
status: ready-for-commit
updated: 2026-04-08
---

# Safe parallel compile report

## Objetivo

Concluir a separação entre geração LLM e persistência do `compile`, habilitar lote paralelo seguro com persistência serial determinística e estender o mesmo contrato para `import-book --compile`.

## Escopo entregue

- `kb/compile.py`
  - `CompileArtifact`, `CompileFailure`, `CompileBatchResult`
  - `compile_to_artifact()` para geração pura
  - `persist_artifact()` para persistência serial
  - `compile_many()` com geração paralela, persistência em ordem de entrada e falhas agregadas
  - `compile_file()` mantido como wrapper compatível
- `kb/cli.py`
  - `kb compile --workers/-j`
  - `kb compile --no-commit/--commit` com default sem commit
  - `import-book --compile` alinhado ao modelo de batch seguro em paralelo
- `kb/jobs.py`
  - job `compile` migrado para `compile_many()`
- Testes
  - cobertura unitária e de integração para lote paralelo, persistência determinística, falha parcial, CLI serial/paralela e compatibilidade de jobs
  - compatibilidade de `pytest` sem override manual de `addopts`

## Validação

- Focada no escopo alterado: `39` testes passando com `pytest-cov`
- Suíte completa: `139` testes passando
- Cobertura real total: `78%`
- Cobertura relevante:
  - `kb/compile.py`: `91%`
  - `kb/cli.py`: `60%`
  - `kb/jobs.py`: `93%`

## Riscos residuais

- Concorrência foi validada com mocks e interleaving controlado; ainda falta validação com provider real sob carga paralela sustentada.
- `kb/cli.py` continua como um dos maiores gaps de cobertura do projeto.
- `kb/git.py` ainda tem cobertura baixa e merece testes de integração dedicados.

## Próximo passo recomendado

1. Validar `compile_many()` contra provider real com mais de um worker.
2. Subir cobertura de `kb/cli.py`, `kb/book_import_core.py` e `kb/git.py`.
3. Revisar se o modelo de commit explícito deve ser harmonizado em outros comandos que ainda usam `--no-commit` como opt-out.
