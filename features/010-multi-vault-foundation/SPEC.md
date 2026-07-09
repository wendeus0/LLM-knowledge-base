---
title: Multi-vault foundation — múltiplos vaults sob um KB_DATA_DIR raiz
epic: infra
status: draft
pr:
---

# Multi-vault foundation — múltiplos vaults sob um KB_DATA_DIR raiz

## Objetivo

Hoje a engine opera sobre um único vault (`KB_DATA_DIR` com `raw/`, `wiki/`, `outputs/`, `kb_state/`); o objetivo é permitir múltiplos vaults nomeados (ex.: `estudo`, `trabalho`, `seguranca`) selecionáveis por invocação, sem misturar corpus, estado ou histórico entre eles.

## Requisitos funcionais

- [ ] RF-01: `kb --vault <nome> <comando>` (ou `KB_VAULT=<nome>`) roteia TODOS os paths (raw/wiki/outputs/archive/kb_state) para o vault nomeado
- [ ] RF-02: sem `--vault`, comportamento atual preservado (vault único = raiz de `KB_DATA_DIR`) — zero breaking change
- [ ] RF-03: `kb vault list` lista vaults existentes sob a raiz; `kb vault create <nome>` cria a estrutura de diretórios de um vault novo
- [ ] RF-04: estado é isolado por vault: manifest, knowledge, learnings, claims, audit e tracking.db não vazam entre vaults
- [ ] RF-05: `KB_TOPICS` pode ser sobrescrito por vault (NEEDS CLARIFICATION: arquivo de config por vault, ex. `<vault>/kb.toml`, ou só env var?)
- [ ] RF-06: templates por vault (`<vault>/templates/*.md`, já suportado pela feature article-template) continuam funcionando com o vault resolvido

## Requisitos técnicos

- RT-01: **Pré-requisito estrutural:** `kb/config.py` resolve todos os paths no import do módulo (module-level). Multi-vault exige resolução em runtime — refatorar para funções acessoras (ex.: `get_paths()` / objeto de contexto) ANTES de qualquer roteamento por vault. Este débito já está registrado no PENDING_LOG (2026-07-09).
- RT-02: Layout proposto: `KB_DATA_DIR/vaults/<nome>/{raw,wiki,outputs,archive,kb_state}`; vault default permanece na raiz de `KB_DATA_DIR` para compatibilidade (NEEDS CLARIFICATION: migrar o vault raiz para `vaults/default/` com comando de migração, ou manter híbrido para sempre?)
- RT-03: Precedência de seleção: flag `--vault` > env `KB_VAULT` > default (raiz)
- RT-04: `tests/conftest.py` monkeypatcha ~24 globais de path de módulos — a refatoração RT-01 deve reduzir isso a um único ponto de patch (benefício colateral esperado)
- RT-05: Git por vault: cada vault pode ser (ou não) um repo git próprio; `kb/git.py::commit` e `kb diff` operam no root do vault selecionado

## Mudanças de API/CLI

- Nova opção global `--vault <nome>` no Typer app (callback) + env `KB_VAULT`
- Novo grupo `kb vault list|create`
- Nenhum comando existente muda de contrato quando `--vault` não é usado

## Testes

- Unit: resolução de paths por vault; precedência flag>env>default; isolamento de state entre dois vaults em tmp_path
- Integration: `ingest → compile → qa` em dois vaults distintos sem contaminação cruzada; `kb stats` reporta apenas o vault selecionado
- Manual: criar segundo vault real, compilar um doc em cada, validar Obsidian apontando para cada wiki

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | ~8-12h (inclui refactor do config.py) |
| Bloqueador | não |
| Risco | médio (refactor de config toca todos os módulos) |

## Dependências

- Refactor `kb/config.py` import-time → runtime (RT-01) — deve ser a primeira fase do PLAN
- Feature article-template (entregue 2026-07-09) — override de templates por vault já assume vault path

## ADR

- Necessária? sim — layout de diretórios multi-vault e estratégia de compatibilidade (RT-02) são decisões duráveis com trade-off. Redigir via `adr-manager` após clarify.

## Critérios de aceite

- [ ] Dois vaults com corpus distintos compilam sem contaminação cruzada (teste de integração prova)
- [ ] `kb --vault x stats` ≠ `kb --vault y stats` com dados distintos
- [ ] Suíte existente passa sem alteração quando `--vault` não é usado
- [ ] `kb vault create novo && kb --vault novo ingest doc.md && kb --vault novo compile` funciona end-to-end

## Evidências esperadas

- Comandos executados:
  - `python -m pytest tests/unit/test_vaults.py tests/integration/test_multi_vault.py`
  - `ruff check kb`
- Arquivos alterados:
  - `kb/config.py` (refactor acessores)
  - `kb/vaults.py` (novo)
  - `kb/cli.py` (opção global + grupo vault)
  - módulos que capturam paths no import (adoção dos acessores)

## Open questions

- NEEDS CLARIFICATION (RF-05): config por vault em arquivo (`kb.toml`) ou só env? Recomendação: arquivo por vault, env como override.
- NEEDS CLARIFICATION (RT-02): migração do vault raiz para `vaults/default/` — obrigatória, opcional via comando, ou nunca?
- NEEDS CLARIFICATION: `kb jobs`/cron operam sobre um vault ou iteram todos? Recomendação: um vault por invocação (`--vault` no cron line).

## Notas

Decisão de origem: dono confirmou em 2026-07-09 que multi-vault é meta real (não drift de doc). Esta SPEC é draft para revisão humana — gate HITL: não avança para task-planner sem aprovação explícita do dono (via `spec-clarify` para as NEEDS CLARIFICATION acima).
