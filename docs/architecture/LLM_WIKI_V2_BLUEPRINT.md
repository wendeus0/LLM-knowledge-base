# LLM Wiki v2 Blueprint (KB)

Blueprint técnico para evoluir o `LLM-knowledge-base` de wiki markdown + keyword search para uma knowledge engine orientada a claims com lifecycle, retrieval híbrido e automação operacional.

## 1) Resumo executivo

Objetivo do blueprint:

- tornar o conhecimento explicitamente versionável e auditável
- evitar degradação da base com tempo (rot, stale facts, contradições silenciosas)
- melhorar qualidade de QA com retrieval híbrido (keyword + semântico + relacional)
- reduzir custo operacional manual via hooks/eventos e jobs canônicos

Resultados esperados:

- respostas mais consistentes e com confiança explícita
- menos duplicidade/incoerência no estado
- evolução progressiva sem quebra da CLI atual

## 2) Princípios arquiteturais

- Claim-first: conhecimento consolidado é representado por claims, não apenas por páginas.
- Lifecycle-aware: confiança e prioridade variam no tempo e por reforço.
- Supersession explícita: informação nova não apaga histórico; supersede com trilha.
- Retrieval multimodal: combinar sinais léxicos, semânticos e estruturais.
- Progressive enhancement: modo compatível por padrão; capacidades novas entram por fase.
- Offline-testable: contratos e algoritmos centrais validados sem provider real.

## 3) Estado alvo (alto nível)

Camadas de memória:

1. working: observações recentes (baixa confiança)
2. episodic: sínteses de sessão
3. semantic: fatos consolidados (claims)
4. procedural: workflows/padrões estáveis

Representações principais:

- wiki pages (leitura humana)
- claim store (verdades operacionais versionadas)
- entity/relation graph (navegação semântica e impacto)
- audit log (rastreabilidade)

## 4) Modelo de dados (contratos JSON)

Todos os contratos abaixo devem ser versionados (`schema_version`) e persistidos em `KB_DATA_DIR/kb_state/`.

### 4.1 claim.json

```json
{
  "schema_version": "1.0",
  "id": "clm_01J...",
  "canonical_text": "Project X uses Redis for caching.",
  "topic": "architecture",
  "status": "active",
  "confidence": 0.82,
  "evidence_count": 3,
  "contradiction_count": 0,
  "sources": [
    {
      "source_id": "src_...",
      "uri": "raw/notes/redis.md",
      "kind": "raw",
      "observed_at": "2026-04-12T20:00:00Z",
      "authority": 0.7
    }
  ],
  "relationships": {
    "supersedes": null,
    "superseded_by": null,
    "contradicts": [],
    "supports": []
  },
  "time": {
    "created_at": "2026-04-12T20:10:00Z",
    "last_confirmed_at": "2026-04-12T20:10:00Z",
    "last_accessed_at": "2026-04-12T20:12:00Z"
  },
  "lifecycle": {
    "decay_profile": "default",
    "ttl_days": 180,
    "stale_after_days": 45
  },
  "provenance": {
    "created_by": "compile",
    "run_id": "run_...",
    "session_id": "sess_..."
  }
}
```

Status permitido:

- `active`: claim vigente
- `stale`: claim com baixa confiança/recência
- `superseded`: claim substituída por claim mais nova
- `disputed`: claim em conflito sem resolução automática

### 4.2 entity.json

```json
{
  "schema_version": "1.0",
  "id": "ent_01J...",
  "name": "Redis",
  "type": "library",
  "aliases": ["redis-db"],
  "attributes": {
    "domain": "cache",
    "criticality": "high"
  },
  "confidence": 0.9,
  "sources": ["src_..."],
  "created_at": "2026-04-12T20:00:00Z",
  "updated_at": "2026-04-12T20:10:00Z"
}
```

### 4.3 relation.json

```json
{
  "schema_version": "1.0",
  "id": "rel_01J...",
  "from_entity": "ent_redis",
  "to_entity": "ent_project_x",
  "type": "used_by",
  "weight": 0.87,
  "evidence_claims": ["clm_..."],
  "created_at": "2026-04-12T20:10:00Z",
  "updated_at": "2026-04-12T20:10:00Z"
}
```

Tipos mínimos de relação:

- `uses`, `depends_on`, `causes`, `fixes`, `contradicts`, `supersedes`, `related_to`

### 4.4 memory_tier_item.json

```json
{
  "schema_version": "1.0",
  "id": "mem_01J...",
  "tier": "episodic",
  "content": "Resumo da sessão ...",
  "linked_claims": ["clm_..."],
  "promotion": {
    "from": "working",
    "to": "episodic",
    "reason": "session_end",
    "score": 0.78
  },
  "created_at": "2026-04-12T21:00:00Z"
}
```

### 4.5 retrieval_result.json

```json
{
  "schema_version": "1.0",
  "query": "impacto de upgrade do Redis",
  "mode": "hybrid",
  "candidates": [
    {
      "id": "clm_...",
      "channel_scores": {
        "keyword": 0.66,
        "semantic": 0.72,
        "graph": 0.81
      },
      "rrf_score": 0.034,
      "rank": 1
    }
  ],
  "top_k": 8,
  "generated_at": "2026-04-12T21:10:00Z"
}
```

## 5) Algoritmos e regras mínimas

### 5.1 Score de confiança (v1 auditável)

`confidence = clamp( base + evidence_boost + recency_boost - contradiction_penalty - decay_penalty )`

Componentes sugeridos:

- `base`: 0.45
- `evidence_boost`: min(0.25, 0.05 * evidence_count)
- `recency_boost`: até 0.15
- `contradiction_penalty`: min(0.35, 0.1 * contradiction_count)
- `decay_penalty`: calculado por curva exponencial por perfil

### 5.2 Decay temporal

`decay_penalty(t) = alpha(profile) * (1 - exp(-lambda(profile) * days_since_last_confirmed))`

Perfis iniciais:

- `architecture` (lento)
- `operational` (médio)
- `bug/transient` (rápido)
- `default`

### 5.3 Supersession

Quando claim nova contradiz claim ativa com score maior por regra determinística:

- marcar antiga como `superseded`
- preencher `superseded_by`
- criar relação `supersedes`
- registrar evento em audit log

Se não houver confiança suficiente para resolver, ambas entram como `disputed`.

### 5.4 Fusion de retrieval (RRF)

Aplicar reciprocal rank fusion sobre três listas ordenadas:

- keyword/BM25
- semantic embedding
- graph traversal

`RRF(d) = Σ_i 1 / (k + rank_i(d))`, com `k` inicial 60.

Degradação graciosa:

- sem embeddings: fusion keyword + graph
- sem graph: fusion keyword + semantic
- sem ambos: keyword only (modo legado)

## 6) Hooks e automação

Eventos canônicos:

- `on_source_added`
  - redaction
  - ingest metadata
  - enqueue extraction
- `on_session_end`
  - gerar item episodic
  - candidate claims
- `on_schedule` (jobs)
  - lifecycle-decay
  - contradiction-check
  - consolidation
  - index-refresh

Sem daemon obrigatório na fase inicial:

- execução via `kb jobs run <job>`
- evolução opcional posterior para scheduler persistente

## 7) Plano por fases

### Fase 1 — Foundation data plane

Escopo:

- claim store + audit log
- contrato JSON v1
- confidence + decay básico
- supersession e disputed state

Saída:

- estado versionado em `kb_state/claims/*.jsonl` e `kb_state/audit/*.jsonl`
- testes unitários de lifecycle

### Fase 2 — Hybrid retrieval plane

Escopo:

- índice keyword/BM25 dedicado
- integração com embeddings (feature flag)
- entity/relation graph mínimo
- fusion RRF no `qa`

Saída:

- `qa` retorna/usa metadados de confiança e origem
- fallback automático para modo parcial

### Fase 3 — Automation + quality plane

Escopo:

- hooks operacionais
- jobs canônicos de manutenção
- políticas de redaction e quality gates
- relatório de saúde do estado (stale %, disputed %, orphan entities)

Saída:

- operação contínua com menor intervenção manual

## 8) Matriz de rastreabilidade (SPEC -> entrega)

- RF-01, RF-02, RF-03 -> Fase 1 + testes de lifecycle
- RF-04 -> Fase 1/3 + promoção de memória
- RF-05 -> Fase 2 + testes de retrieval
- RF-06 -> Fase 3 + jobs
- RF-07 -> Fase 1 + audit log
- RF-08 -> Fase 3 + redaction

## 9) Riscos e mitigação

1. Complexidade operacional crescente
- Mitigação: flags progressivas e fallback legado

2. Incerteza em resolução automática de contradições
- Mitigação: estado `disputed` + revisão humana opcional

3. Custo de indexação/embeddings
- Mitigação: modo on-demand + cache + feature flag

4. Drift de schema
- Mitigação: `schema_version` + migradores explícitos

## 10) Critérios de pronto (DoD da fundação)

- contratos JSON v1 documentados e testados
- ADR aprovada com decisão claim-centric + hybrid retrieval
- roadmap faseado com ordem de implementação e riscos
- compatibilidade com CLI atual preservada por padrão

## 11) Arquivos e diretórios sugeridos

No engine (repo):

- `kb/lifecycle.py` (score, decay, supersession)
- `kb/claims.py` (CRUD de claims + validação)
- `kb/retrieval.py` (fusion + fallback)
- `kb/graph.py` (entities/relations)
- `kb/audit.py` (append-only audit)

No `KB_DATA_DIR/kb_state/`:

- `claims/claims.jsonl`
- `claims/relations.jsonl`
- `claims/entities.jsonl`
- `memory/working.jsonl`
- `memory/episodic.jsonl`
- `memory/semantic.jsonl`
- `memory/procedural.jsonl`
- `audit/events.jsonl`

## 12) Próximo lote recomendado (implementação)

1. Implementar contratos + persistência append-only (Fase 1)
2. Adicionar testes RED/GREEN de confidence/decay/supersession
3. Integrar extração de claims no compile
4. Expor leitura de claims no qa (modo compatível)
5. Só depois ativar retrieval híbrido completo