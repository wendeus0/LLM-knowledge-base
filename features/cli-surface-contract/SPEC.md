---
title: CLI surface contract
epic: infra
status: approved
pr:
---

# CLI surface contract

## Objetivo

A CLI já concentra diversos fluxos (`ingest`, `compile`, `qa`, `search`, `lint`, `heal`, `jobs`), porém sem SPEC consolidada de interface pública e contratos de flags; esta feature formaliza o contrato para reduzir drift e fechar parcial documental.

## Requisitos funcionais

- [ ] RF-01: comandos públicos suportados devem incluir `ingest`, `import-book`, `compile`, `qa`, `search`, `lint`, `heal`, `jobs list`, `jobs run`
- [ ] RF-02: fluxos com provider externo devem oferecer caminho seguro padrão e confirmação para conteúdo sensível quando aplicável
- [ ] RF-03: fluxos com write devem suportar controle de commit via flag (`--no-commit` ou `--no-commit/--commit` conforme contrato de cada comando)
- [ ] RF-04: `kb search` deve imprimir lista de resultados ou `Nenhum resultado encontrado.`
- [ ] RF-05: `kb jobs list` deve listar `nome`, `schedule` e `description`; `kb jobs run <nome>` executa e imprime retorno

## Requisitos técnicos

- RT-01: camada CLI deve delegar implementação para `kb/cmds/*` ou módulos de domínio, evitando duplicação de regra de negócio
- RT-02: mensagens de erro para usuário devem ser explícitas e acionáveis
- RT-03: manter compatibilidade com Typer + Rich sem breaking changes na interface existente

## Mudanças de API/CLI

- Não adiciona comando novo; formaliza contrato da superfície atual.

## Testes

- Unit:
  - `tests/unit/test_cli.py`
  - `tests/unit/test_compile_cmds.py`
  - `tests/unit/test_qa_cmds.py`
  - `tests/unit/test_lint_cmds.py`
- Integration:
  - `tests/integration/test_sensitive_execution_cli.py`
  - `tests/integration/test_book_import_cli.py`
- Manual:
  1. `kb --help`
  2. `kb search "xss"`
  3. `kb jobs list`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 3h |
| Bloqueador | não |
| Risco | médio |

## Dependências

- `docs/adr/0002-typer-cli-framework.md`
- `features/sensitive-execution-controls/SPEC.md`

## ADR

- Necessária? não

## Critérios de aceite

- [ ] `kb/cli.py` deixa de estar em `PARCIAL` na matriz por ausência de SPEC consolidada
- [ ] suíte unitária de CLI permanece verde

## Evidências esperadas

- `python -m pytest tests/unit/test_cli.py tests/unit/test_compile_cmds.py tests/unit/test_qa_cmds.py tests/unit/test_lint_cmds.py -q`

## Notas

Contrato de UX textual detalhado pode evoluir em documento dedicado de design CLI sem alterar esta SPEC base.
