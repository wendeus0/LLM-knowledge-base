---
title: Multi-vault foundation — múltiplos vaults sob um KB_DATA_DIR raiz
epic: infra
status: draft
pr:
---

# Multi-vault foundation — múltiplos vaults sob um KB_DATA_DIR raiz

## Objetivo

Hoje a engine opera sobre um único vault (`KB_DATA_DIR` com `raw/`, `wiki/`, `outputs/`, `kb_state/`); o objetivo é permitir múltiplos vaults nomeados selecionáveis por invocação, sem misturar corpus, estado ou histórico entre eles.

Casos de uso confirmados pelo dono (2026-07-09, clarify): separar domínios de estudo (wikis independentes com topics próprios), compartilhar um vault público mantendo os demais privados, e vault descartável para experimentação segura de compile/heal/templates.

## Requisitos funcionais

- [ ] RF-01: `kb --vault <nome> <comando>` (ou `KB_VAULT=<nome>`) roteia TODOS os paths (raw/wiki/outputs/archive/kb_state) para o vault nomeado
- [ ] RF-02: sem `--vault`, os comandos operam no vault `default` (`vaults/default/`, resultado da migração obrigatória de RT-02); antes da migração, comandos falham com mensagem clara orientando `kb vault migrate`
- [ ] RF-03: `kb vault list` lista vaults existentes sob a raiz; `kb vault create <nome>` cria a estrutura de diretórios de um vault novo
- [ ] RF-04: estado é isolado por vault: manifest, knowledge, learnings, claims, audit e tracking.db não vazam entre vaults
- [ ] RF-05: config por vault em `<vault>/kb.toml` (topics, modelo, ajustes), com env vars como override global; vault sem arquivo herda defaults — decisão do dono (2026-07-09, clarify)
- [ ] RF-06: templates por vault (`<vault>/templates/*.md`, já suportado pela feature article-template) continuam funcionando com o vault resolvido
- [ ] RF-07: `kb vault migrate` migra o vault raiz para `vaults/default/` com `--dry-run`, confirmação interativa e manifest de backup (ver RT-02)

## Requisitos técnicos

- RT-01: **Pré-requisito estrutural:** `kb/config.py` resolve todos os paths no import do módulo (module-level). Multi-vault exige resolução em runtime — refatorar para funções acessoras (ex.: `get_paths()` / objeto de contexto) ANTES de qualquer roteamento por vault. Este débito já está registrado no PENDING_LOG (2026-07-09).
- RT-02: Layout: `KB_DATA_DIR/vaults/<nome>/{raw,wiki,outputs,archive,kb_state}`. **Migração do vault raiz para `vaults/default/` é obrigatória** (decisão do dono, 2026-07-09), com salvaguardas inegociáveis: (a) `--dry-run` mostra o plano antes; (b) a migração real exige confirmação interativa explícita; (c) manifest de backup do estado pré-migração; (d) output final imprime o novo path da wiki com instrução de reapontar o vault do Obsidian (`<KB_DATA_DIR>/vaults/default/wiki`); (e) nunca migrar silenciosamente no meio de outro comando — layout antigo detectado → erro orientando `kb vault migrate`
- RT-03: Precedência de seleção: flag `--vault` > env `KB_VAULT` > vault `default`
- RT-04: `tests/conftest.py` monkeypatcha ~24 globais de path de módulos — a refatoração RT-01 deve reduzir isso a um único ponto de patch (benefício colateral esperado)
- RT-05: Git por vault: cada vault pode ser (ou não) um repo git próprio; `kb/git.py::commit` e `kb diff` operam no root do vault selecionado

## Mudanças de API/CLI

- Nova opção global `--vault <nome>` no Typer app (callback) + env `KB_VAULT`
- Novo grupo `kb vault list|create|migrate`
- Contratos de flags dos comandos existentes não mudam; **breaking change consciente:** após o upgrade, o layout antigo exige `kb vault migrate` uma única vez (RT-02) — mudança de major/minor com nota destacada no CHANGELOG

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

## Decisões de clarify (2026-07-09, entrevista com o dono)

- RF-05: config por vault em `<vault>/kb.toml`, env vars como override global.
- RT-02: migração do vault raiz para `vaults/default/` é **obrigatória**, com dry-run + confirmação + backup + instrução de reapontar o Obsidian.
- Jobs/cron: **um vault por invocação** — cada linha de cron declara `--vault`; `kb jobs cron` gera as linhas por vault.
- Casos de uso priorizados: separar domínios de estudo, compartilhar um vault, experimentação segura.

## Notas

Decisão de origem: dono confirmou em 2026-07-09 que multi-vault é meta real (não drift de doc). Clarify realizado em entrevista na mesma data (seção acima) — sem questões abertas. Gate HITL restante: aprovação final da SPEC pelo dono antes de `task-planner`.
