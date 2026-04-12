# RTK-Style Blueprint para o kb

Objetivo: incorporar os princípios arquiteturais do RTK no kb sem rewrite total, em migração incremental, preservando comportamento atual.

## 1) Princípios copiados do RTK

- Contratos fortes de execução:
  - preservar exit code
  - fallback para saída crua quando filtro falhar
  - tracking em toda execução
- Separação por camadas:
  - `cmds/` (lógica por comando)
  - `core/` (infra compartilhada)
  - `discover/` (classificação/roteamento)
  - `analytics/` (visão de ganhos)
- Extensão previsível:
  - regra clara para adicionar comando novo
  - ponto único de classificação

## 2) Estado atual (resumo)

- CLI concentrada em `kb/cli.py`
- Lógica funcional distribuída em módulos de domínio (`compile.py`, `qa.py`, `heal.py`, etc.)
- Testes fortes já existentes
- Documentação/ADR já madura

## 3) Estrutura alvo (incremental)

```text
kb/
  cli/
    app.py
    commands/
      ingest.py
      compile.py
      qa.py
      heal.py
      lint.py
      jobs.py
  cmds/
    ingest/run.py
    compile/run.py
    qa/run.py
    heal/run.py
  core/
    runner.py
    tracking.py
    output_filter.py
    failover.py
    config.py
  discover/
    rules.py
    registry.py
  analytics/
    gain.py
    history.py
```

Obs: na primeira etapa, manteremos compatibilidade com `kb/cli.py` atual e vamos introduzir `core/` + `discover/` sem quebrar imports.

## 4) O que já foi scaffoldado nesta fase

- `kb/core/__init__.py`
- `kb/core/runner.py`
- `kb/core/tracking.py`
- `kb/discover/__init__.py`
- `kb/discover/rules.py`
- `kb/discover/registry.py`

Esses arquivos formam a “casca RTK” para execução/medição/classificação.

## 5) Sequência de commits recomendada

### Commit 1 — foundation/core

Arquivos:
- `kb/core/*`

Mensagem sugerida:
- `feat(core): add RTK-style runner and SQLite tracking foundation`

### Commit 2 — foundation/discover

Arquivos:
- `kb/discover/*`

Mensagem sugerida:
- `feat(discover): add internal command classification registry`

### Commit 3 — docs/blueprint

Arquivos:
- `docs/architecture/RTK_STYLE_BLUEPRINT.md`

Mensagem sugerida:
- `docs(architecture): add RTK-style migration blueprint`

### Commit 4 — integração do primeiro comando (piloto)

Alvo inicial recomendado:
- `search` (mais simples/baixo risco)

Passos:
1. Encapsular execução em `kb/cmds/search/run.py`
2. Aplicar `core.runner.run_command` com filtro básico
3. Chamar novo módulo no `kb/cli.py` sem remover caminho antigo
4. Cobrir com testes unitários

Mensagem sugerida:
- `refactor(search): adopt shared runner with fail-safe filtering and tracking`

### Commit 5 — analytics CLI

Adicionar comando:
- `kb jobs run metrics` ou `kb analytics gain`

Base:
- `kb.core.tracking.get_gain_summary()`

Mensagem sugerida:
- `feat(analytics): expose token savings summary from tracking database`

## 6) Guardrails de migração

- Não mexer em comportamento funcional dos comandos na mesma mudança estrutural
- Uma vertical por vez (search → qa → compile ...)
- Sempre validar:
  - exit code preservado
  - fallback ativo
  - tracking gravado

## 7) Critérios de pronto da Fase 1

- [x] Camada `core` criada
- [x] Camada `discover` criada
- [x] Documento de blueprint criado
- [x] Primeiro comando migrado para camada `cmds` (piloto: `search`)
- [x] Comando de analytics exposto via `jobs run metrics`

## 8) Próximas ações recomendadas

1. Migrar `lint` para `kb/cmds/lint/run.py` mantendo semântica atual.
2. Migrar `jobs` para consumir `discover.registry` (classificação central).
3. Introduzir `kb/analytics/history.py` para consultas históricas por comando/período.
4. Migrar `qa` e `compile` por último (maior acoplamento/guardrails).
