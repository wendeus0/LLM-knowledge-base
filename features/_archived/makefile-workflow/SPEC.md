---
title: Makefile workflow
epic: infra
status: approved
pr:
---

# Makefile workflow

## Objetivo

Hoje o repositório documenta fluxos recorrentes de instalação, lint, testes e execução de comandos `kb`, mas não oferece uma interface única para esses atalhos; esta frente adiciona um `Makefile` enxuto para padronizar o workflow local sem introduzir um diretório `scripts/`.

## Requisitos funcionais

- [ ] RF-01: o repositório deve expor um alvo `help` listando os comandos canônicos disponíveis no `Makefile`
- [ ] RF-02: o `Makefile` deve cobrir os fluxos recorrentes de setup, lint e testes já documentados no projeto
- [ ] RF-03: o `Makefile` deve expor atalhos mínimos para comandos operacionais frequentes do CLI `kb` sem alterar sua semântica
- [ ] RF-04: a documentação de contribuição/uso deve refletir a existência do `Makefile` e quando usá-lo

## Requisitos técnicos

- RT-01: preferir `Makefile` a `scripts/` para manter baixo overhead operacional
- RT-02: manter os comandos como thin wrappers sobre `pip`, `python -m pytest`, `ruff` e `kb`
- RT-03: evitar lógica condicional complexa, autodiscovery ou dependência externa nova

## Mudanças de API/CLI

- Superfície nova de desenvolvimento local: `make <target>`
- Nenhuma mudança na CLI pública `kb`

## Testes

- Manual:
  1. `make help`
  2. `make lint`
  3. `make test-unit`

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 2h    |
| Bloqueador | não   |
| Risco      | baixo |

## Dependências

- `README.md`
- `CONTRIBUTING.md`
- `pyproject.toml`

## ADR

- Necessária? não
- Se sim, referência: não aplicável

## Critérios de aceite

- [ ] o repositório passa a ter uma entrada única para setup/test/lint sem duplicar lógica em scripts avulsos
- [ ] o `Makefile` permanece pequeno e previsível, cobrindo apenas fluxos recorrentes já estabelecidos
- [ ] README e guia de contribuição apontam para o novo atalho operacional

## Evidências esperadas

- Comandos executados:
  - `make help`
  - `make lint`
  - `make test-unit`
- Arquivos alterados:
  - `Makefile`
  - `README.md`
  - `CONTRIBUTING.md`

## Notas

Não inclui automação de release, compose de jobs complexos nem substituição da CLI `kb`.
