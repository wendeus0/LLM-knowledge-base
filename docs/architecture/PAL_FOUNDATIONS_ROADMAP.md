# Roadmap — Pal-inspired foundations for `kb`

## Objetivo

Adaptar ao `kb` as capacidades mais valiosas observadas em `agno-agi/pal`, sem descaracterizar a arquitetura local baseada em CLI + markdown + git.

## Estado atual do `kb`

| Capability | Estado atual | Gap para a visão alvo |
|---|---|---|
| Routing por fonte | `qa` consulta apenas `wiki/` via busca lexical | Falta roteamento explícito entre `wiki/`, `raw/`, memória operacional e metadados compilados |
| Memória separada | existe memória operacional da sessão em `memory/`, mas não memória funcional do produto | Falta separar artefatos de produto em `knowledge` vs `learnings` |
| Ingestão + compilação | `raw/ -> wiki/` já existe | Falta registrar manifestos, resumos compilados e índice utilizável pelo roteador |
| Guardrails | regras documentadas, mas pouco enforcement em runtime | Falta confirmação ativa antes de enviar conteúdo sensível ao provider e antes de file-back sensível |
| Evals automatizadas | suíte pytest existente | Falta suíte focada em routing, guardrails, memória e jobs |
| Jobs agendados | inexistente no produto | Falta catálogo de jobs e mecanismo canônico de execução |
| Multi-agent specialization | não existe | Fica fora da fase inicial |

## Escopo da fase inicial

Implementar agora:

1. **routing por fonte nativa**
2. **memória separada em knowledge vs learnings**
3. **pipeline de ingestão + resumo compilado**
4. **guardrails + confirmações**
5. **evals automatizadas**
6. **jobs agendados**

Implementar depois:

7. **multi-agent specialization**

## Estratégia de entrega

### Fase 1 — Foundation slice (agora)

Entregar uma base funcional e pequena:

- classificador simples de rota para `qa`
- store local para `knowledge` e `learnings`
- manifest/summary de compilação
- guardrails de conteúdo sensível antes de chamadas LLM e file-back
- jobs declarativos (`list` + `run`)
- testes automáticos dos novos fluxos

### Fase 2 — Robustez

- enriquecer roteamento com scoring por fonte
- guardar learnings explícitos de correções do usuário
- promover summaries a camada de navegação mais forte
- dry-run/no-commit para fluxos sensíveis
- relatórios de jobs com persistência

### Fase 3 — Futuro

- scheduler externo/documentado (`cron`, systemd timer, GitHub Actions local/CI)
- ranking híbrido lexical + embeddings
- lint de knowledge/learnings
- especialização multi-agent para ingest/compile/qa/lint

## Feature mapping detalhado

### 1. Routing por fonte nativa

**Implementação inicial**
- Introduzir roteador heurístico para `qa`
- Fontes iniciais: `wiki`, `raw`, `knowledge`, `learnings`
- Expor decisão de rota de forma auditável em testes

**Futuro**
- ranking híbrido e fallback multi-source
- explicação de rota ao usuário via flag `--debug-route`

### 2. Memória separada em knowledge vs learnings

**Implementação inicial**
- `knowledge`: fatos compilados, manifestos, summaries, índice de artefatos
- `learnings`: correções/padrões operacionais reutilizáveis

**Futuro**
- learnings explícitos via comando dedicado (`kb learn`)
- TTL/pruning e lint da memória

### 3. Pipeline de ingestão + resumo compilado

**Implementação inicial**
- registrar ingest em manifesto versionado
- gerar summary markdown junto do artigo compilado
- atualizar índice/knowledge store

**Futuro**
- summaries por conceito e por documento
- compilação incremental orientada por manifesto

### 4. Guardrails + confirmações

**Implementação inicial**
- detectar padrões sensíveis em `compile`, `qa`, `heal`, `lint`, `qa --file-back`
- exigir confirmação explícita para seguir com provider externo

**Futuro**
- níveis de sensibilidade
- modo `--allow-sensitive` / `--no-commit`
- políticas por diretório (`raw/private/`, por exemplo)

### 5. Evals automatizadas

**Implementação inicial**
- testes unitários para roteamento, guardrails e stores
- testes de integração para compile -> summary -> knowledge e jobs

**Futuro**
- golden tests de prompts
- smoke test opcional com provider real

### 6. Jobs agendados

**Implementação inicial**
- catálogo fixo de jobs: `compile`, `lint`, `review`
- comando `kb jobs list`
- comando `kb jobs run <job>`

**Futuro**
- geração de crontab/systemd snippets
- tracking de última execução

### 7. Multi-agent specialization

**Futuro explícito**
- manter fora do escopo da primeira implementação
- só considerar após estabilizar routing, memória e guardrails

## Features futuras registradas

- embeddings + RAG híbrido
- integração Obsidian com comandos do `kb`
- sync/remoto orientado a políticas
- lint/health check de `knowledge` e `learnings`
- explicabilidade de routing no CLI
- modo sem commit para cenários sensíveis
- especialização multi-agent (`navigator`, `compiler`, `linter`, etc.)
