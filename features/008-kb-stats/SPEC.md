---
title: kb stats — Dashboard de métricas da wiki
epic: infra
status: done
pr:
---

# kb stats — Dashboard de métricas da wiki

## Objetivo

Expor via CLI as métricas já calculadas em `kb/analytics/` (health, history) como um dashboard Rich com tabelas e barras de progresso, dando visão rápida do estado da wiki.

## Requisitos funcionais

- [x] RF-01: `kb stats` deve exibir resumo de claims (total, active, stale, disputed, superseded, avg_confidence)
- [x] RF-02: `kb stats` deve exibir histórico de comandos dos últimos 7 dias (total runs, failures, avg duration)
- [x] RF-03: `kb stats` deve exibir contagem de artigos em wiki/ (total, por tópico se disponível)
- [x] RF-04: saída formatada com Rich (tabelas, barras de progresso para pct de active/stale)
- [x] RF-05: flag `--json` para saída machine-readable

## Requisitos técnicos

- RT-01: reutilizar `kb/analytics/health.py`, `kb/analytics/history.py`
- RT-02: reutilizar `kb/claims.py` para contagem de claims
- RT-03: contagem de artigos via `WIKI_DIR.rglob("*.md")`

## Mudanças de API/CLI

Novo comando `kb stats [--json]`. Sem breaking changes.

## Testes

- Unit: formatação de saída, flags, contagem de artigos com wiki fixture
- Integration: `kb stats` com vault de teste populado

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | ~3h |
| Bloqueador | não |
| Risco | baixo |

## Dependências

- `kb/analytics/` (já existe)
- `kb/claims.py` (já existe)

## ADR

- Necessária? não

## Critérios de aceite

- [x] `kb stats` exibe tabela com contagem de claims por status
- [x] `kb stats` exibe métricas de history dos últimos 7 dias
- [x] `kb stats --json` produz JSON parseable
- [x] `kb stats` funciona com vault vazio (zeros)

## Evidências esperadas

- Comandos executados:
  - `python -m pytest tests/unit/test_stats.py`
  - `ruff check kb`
- Arquivos alterados:
  - `kb/cli.py` (novo comando)
  - `kb/stats.py` (novo módulo)
  - `tests/unit/test_stats.py` (novos testes)

## Notas

Primitivas já existem em `kb/analytics/`. Esta feature é essencialmente camada de apresentação CLI + orquestração.
