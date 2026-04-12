# ADR 0013 — Fundação claim-centric com lifecycle e retrieval híbrido

- Status: Aceito
- Data: 2026-04-12

## Contexto

O `LLM-knowledge-base` já opera com pipeline funcional (ingest/compile/qa/heal/lint), porém com representação principal em markdown e recuperação majoritariamente por palavra-chave.

Esse desenho funciona para escala pequena e média, mas apresenta limites conhecidos quando o volume de conhecimento cresce:

1. fatos antigos permanecem com o mesmo peso de fatos recentes
2. contradições viram texto solto sem resolução operacional
3. atualização de conhecimento é pouco rastreável em nível de claim
4. keyword-only retrieval perde conexões semânticas e estruturais
5. operação depende de rotinas manuais para manter qualidade

A proposta LLM Wiki v2 (Karpathy + extensões de produção) aponta os pilares para resolver esses limites: lifecycle de memória, supersession explícita, estruturas de grafo e busca híbrida.

## Decisão

Adotar fundação arquitetural claim-centric em três eixos complementares:

1) Representação de conhecimento
- Introduzir `claim` como unidade canônica de conhecimento consolidado, com:
  - confidence
  - recência
  - evidências
  - status de lifecycle (`active`, `stale`, `superseded`, `disputed`)
- Manter páginas wiki para legibilidade humana, mas desacoplar verdade operacional da prosa.

2) Lifecycle e governança
- Implementar decaimento temporal de confiança com reforço por reconfirmação.
- Resolver atualização contraditória por supersession explícita quando houver evidência suficiente.
- Persistir trilha auditável de mutações de conhecimento (append-only).

3) Retrieval para QA
- Evoluir `qa` para retrieval híbrido por fusão de:
  - keyword/BM25
  - semântico (embeddings)
  - relacional (grafo de entidades/relações)
- Aplicar fallback progressivo para manter compatibilidade quando uma das capacidades não estiver disponível.

## Escopo e rollout

A decisão é aplicada em rollout incremental por fases:

- Fase 1: data plane (claims + lifecycle + audit)
- Fase 2: retrieval híbrido
- Fase 3: automação operacional e quality gates

Sem breaking change obrigatório na CLI na fase inicial.

## Consequências

### Positivas

- maior consistência de resposta com confiança explícita
- melhor manutenção da base no tempo (menos rot/stale sem controle)
- rastreabilidade forte de por que um fato foi promovido/superseded
- melhora de recuperação de contexto em perguntas de impacto e dependência
- base pronta para evolução multi-agent sem refatoração total

### Negativas

- aumento de complexidade de estado (stores e índices adicionais)
- mais custo computacional em indexação e ranking híbrido
- necessidade de política clara de schema/migração
- risco de heurísticas iniciais de confiança precisarem recalibração

## Alternativas consideradas

### A1. Manter markdown como única fonte de verdade
- Rejeitada. Limita governança, rastreabilidade e resolução de conflito em escala.

### A2. Migrar direto para vector-only retrieval
- Rejeitada. Perde precisão léxica e conexões estruturais; reduz explicabilidade.

### A3. Introduzir apenas grafo sem claims estruturadas
- Rejeitada. Grafo sem lifecycle de claim resolve navegação, mas não governança temporal.

## Implementação vinculada

- SPEC: `features/llm-wiki-v2-foundation/SPEC.md`
- Blueprint: `docs/architecture/LLM_WIKI_V2_BLUEPRINT.md`

Módulos sugeridos para implementação:

- `kb/claims.py`
- `kb/lifecycle.py`
- `kb/retrieval.py`
- `kb/graph.py`
- `kb/audit.py`

Estado sugerido em `KB_DATA_DIR/kb_state/`:

- `claims/*.jsonl`
- `memory/*.jsonl`
- `audit/events.jsonl`

## Quando revisitar

- após primeira calibração de confiança em corpus real
- ao ativar embeddings em produção para avaliar custo/benefício
- ao introduzir colaboração multi-agente com sincronização remota
- se houver necessidade de políticas regulatórias adicionais de retenção/auditoria