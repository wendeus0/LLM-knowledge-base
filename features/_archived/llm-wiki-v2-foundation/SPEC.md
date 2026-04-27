---
title: LLM Wiki v2 foundation (claim lifecycle + hybrid retrieval + automation hooks)
epic: infra
status: draft
pr:
---

# LLM Wiki v2 foundation (claim lifecycle + hybrid retrieval + automation hooks)

## Objetivo

Hoje o `kb` entrega base funcional de ingest/compile/qa/heal/lint com foco em markdown + busca por palavra-chave; esta feature define e implementa a fundação para evolução do produto para um knowledge base orientado a claims com ciclo de vida, recuperação híbrida e automação por eventos, mantendo compatibilidade progressiva com a CLI atual.

## Requisitos funcionais

- [ ] RF-01: o sistema deve representar conhecimento consolidado como `claims` versionáveis com metadados mínimos de confiança, recência, evidência e status (`active`, `stale`, `superseded`, `disputed`).
- [ ] RF-02: ao detectar conflito entre claim nova e claim existente, o sistema deve registrar supersession explícita (`supersedes`) e preservar histórico auditável.
- [ ] RF-03: o sistema deve aplicar decaimento temporal de confiança por tipo de claim, com reforço quando houver reconfirmação por novas evidências.
- [ ] RF-04: o sistema deve separar e promover memória em camadas (`working`, `episodic`, `semantic`, `procedural`) com regras determinísticas mínimas de promoção.
- [ ] RF-05: `kb qa` deve suportar retrieval híbrido com fusão de resultados de keyword/BM25, semântico (embeddings) e relacional (grafo), com fallback seguro para capacidade parcial.
- [ ] RF-06: o sistema deve expor hooks operacionais para eventos (`on_source_added`, `on_session_end`, `on_schedule`) sem exigir daemon residente na fase inicial.
- [ ] RF-07: deve existir trilha de auditoria de mutações de conhecimento (claim create/update/supersede/status-change) com timestamp e origem.
- [ ] RF-08: o fluxo de ingestão deve permitir política de redaction para conteúdo sensível antes da persistência em stores de conhecimento.

## Requisitos técnicos

- RT-01: manter separação engine × corpus (`KB_DATA_DIR`) e evitar acoplamento do estado de usuário ao repositório.
- RT-02: introduzir stores estruturados em `kb_state/` sem quebrar leitura de artefatos já existentes.
- RT-03: preservar comportamento atual de comandos em modo compatível quando novas capacidades não estiverem habilitadas.
- RT-04: especificar contrato JSON versionado para `claim`, `entity`, `relation`, `memory_tier` e `retrieval_result`.
- RT-05: modelar decaimento e score de confiança com funções determinísticas inicialmente simples e auditáveis.
- RT-06: manter estratégia offline-first de testes (sem chamadas reais ao provider).
- RT-07: preparar boundary para introdução progressiva de índices BM25/embeddings/grafo sem reescrever interface de `qa`.

## Mudanças de API/CLI

Compatível por padrão; sem breaking imediato.

Mudanças planejadas por fase:

- Fase 1 (fundação de dados): sem novos comandos obrigatórios; comportamento interno e novos artefatos de estado.
- Fase 2 (retrieval híbrido): expansão de `kb qa` com flags opcionais de estratégia (ex.: `--retrieval-mode`), mantendo default retrocompatível.
- Fase 3 (operação/lifecycle): novos jobs canônicos para decay/consolidação/reindex, acessíveis em `kb jobs`.

## Testes

- Unit:
  - score/decaimento de confiança por tipo de claim
  - detecção de conflito e criação de relação `supersedes`
  - promoção de memória entre tiers
  - fusão de ranking híbrido com degradação graciosa
  - redaction policy aplicada no ingest
- Integration:
  - ingest -> compile -> claim extraction -> qa com retrieval híbrido
  - sessão -> episodic -> semantic -> procedural (com thresholds)
  - jobs de manutenção (decay/consolidation/lint) atualizando estado
- Manual:
  1. `kb ingest <arquivo>`
  2. `kb compile`
  3. `kb qa "qual o impacto de X em Y?"`
  4. `kb jobs list`
  5. `kb jobs run decay`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 24-40h (3 fases) |
| Bloqueador | não |
| Risco | alto |

## Dependências

- `features/pal-foundation-phase-1/SPEC.md`
- `features/search-keyword-contract/SPEC.md`
- `features/jobs-and-git-operational-contract/SPEC.md`
- ADR de arquitetura para lifecycle + retrieval híbrido

## ADR

- Necessária? sim
- Se sim, referência: `docs/adr/0013-claim-centric-lifecycle-and-hybrid-retrieval-foundation.md`

## Critérios de aceite

- [ ] Critério 1: blueprint técnico versionado em `docs/architecture` com fases, contratos e plano de rollout.
- [ ] Critério 2: ADR aceita descrevendo decisão e trade-offs de arquitetura.
- [ ] Critério 3: matriz de rastreabilidade SPEC -> artefatos -> testes definida para execução incremental.

## Evidências esperadas

- Comandos executados:
  - `python -m pytest tests/unit/test_*` (fases de implementação)
  - `ruff check kb`
- Arquivos alterados:
  - `features/llm-wiki-v2-foundation/SPEC.md`
  - `docs/architecture/LLM_WIKI_V2_BLUEPRINT.md`
  - `docs/adr/0013-claim-centric-lifecycle-and-hybrid-retrieval-foundation.md`

## Notas

A entrega atual desta feature cobre blueprint + contratos + decisões arquiteturais. Implementação de código segue em lotes incrementais guiados por TDD.