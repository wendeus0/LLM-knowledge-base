---
title: Lint report contract
epic: lint
status: approved
pr:
---

# Lint report contract

## Objetivo

`kb lint` já audita a wiki e retorna relatório em markdown, mas sem SPEC dedicada do contrato de saída e dos componentes mínimos do relatório; esta feature formaliza esse contrato para reduzir ambiguidade e remover parcial documental.

## Requisitos funcionais

- [ ] RF-01: `kb lint` deve analisar artigos markdown em `WIKI_DIR`; para wiki vazia deve retornar mensagem explícita
- [ ] RF-02: o fluxo deve incluir detecção local de wikilinks quebrados e anexar essa seção ao relatório
- [ ] RF-03: o relatório principal deve ser retornado como string markdown
- [ ] RF-04: quando conteúdo sensível for detectado e `--allow-sensitive` não estiver ativo, o fluxo deve manter comportamento seguro com confirmação/bloqueio
- [ ] RF-05: `kb cmds lint` deve preservar repasse correto de flag `allow_sensitive`

## Requisitos técnicos

- RT-01: detecção local de links quebrados via regex deve ocorrer sem depender do provider
- RT-02: auditoria semântica (inconsistências/lacunas/oportunidades) permanece delegada ao provider LLM
- RT-03: contrato do retorno de `lint_wiki` permanece `str`

## Mudanças de API/CLI

- Sem novos comandos; formaliza comportamento de:
  - `kb lint [--allow-sensitive]`
  - `execute_lint_command(allow_sensitive: bool) -> str`

## Testes

- Unit:
  - `tests/unit/test_lint.py`
  - `tests/unit/test_lint_cmds.py`
- Integration:
  - cenários CLI com guardrails em `tests/integration/test_sensitive_execution_cli.py`
- Manual:
  1. `kb lint`
  2. `kb lint --allow-sensitive`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2h |
| Bloqueador | não |
| Risco | baixo |

## Dependências

- `features/pal-foundation-phase-1/SPEC.md`
- `features/sensitive-execution-controls/SPEC.md`

## ADR

- Necessária? não

## Critérios de aceite

- [ ] `kb/lint.py` deixa de estar em `PARCIAL` por falta de contrato dedicado
- [ ] testes unitários de lint seguem verdes

## Evidências esperadas

- `python -m pytest tests/unit/test_lint.py tests/unit/test_lint_cmds.py -q`

## Notas

Este contrato não impõe schema rígido do markdown do provider; exige apenas componentes mínimos e comportamento operacional previsível.
