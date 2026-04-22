---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **Iniciar `llm-wiki-v2-foundation` em branch dedicada**
   - Status atual: PLAN_READY → próximo: `test-red`
   - `kb/audit.py` + `tests/unit/test_audit.py` já commitados (RF-07 entregue parcialmente)

2. **Criar `tests/unit/test_discovery.py`**
   - `kb/discovery.py` cobertura 25% — módulo novo (PR #34) sem testes dedicados

## Backlog priorizado (3 ondas — triagem 2026-04-22)

### Onda 1 — features pequenas, alto retorno (após v2-foundation desbloquear)

| # | Feature | Esforço | Status |
|---|---------|---------|--------|
| 007 | `kb watch` (compile automático via watchdog) | ~4h | idéia — sem SPEC |
| 008 | `kb stats` (dashboard Rich) | ~3h | SPEC draft |
| 009 | `kb diff` (git diff formatado) | ~2h | SPEC draft |
| 010 | ingest DOCX | ~3h | idéia — sem SPEC |

### Onda 2 — features grandes (após v2-foundation entregar contratos estáveis)

| # | Feature | Esforço | Bloqueio |
|---|---------|---------|----------|
| 011 | `kb export` (HTML/PDF/EPUB) | ~6-8h | nenhum |
| 012 | MCP Server | ~8-12h + ADR | depende de v2 expor claims/retrieval |
| 013 | ingest RSS/Atom | ~4h | depende de hook `on_schedule` (RF-06 v2) |
| 014 | ingest CSV/TSV | ~2h | nice-to-have, valor limitado |

### Descartado

- **BM25 / semântica** como feature isolada — BM25 já entregue em `kb/search.py:42-86`. Parte semântica (embeddings) é RF-05 de `llm-wiki-v2-foundation`.

## Médio prazo (P2 herdado)

3. **Validar `compile_many()` contra provider real** com `--workers 4`
4. **Refinar guardrail de credenciais** (falso positivo em nomes de variável)
5. **Completar separação engine vs. corpus** (neutralizar refs históricas em ADRs)
6. **Embeddings + RAG híbrido** — reavaliar quando wiki > ~200 artigos

## Bloqueadores

Nenhum. Baseline verde: 308/308 testes, 92% cobertura, ruff clean, main alinhada.
