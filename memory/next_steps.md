---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato

1. **Executar o plano de robustez** — `docs/superpowers/plans/2026-07-09-core-robustness.md`, fase a fase (Fase 0 em curso na branch `chore/truth-sync`). Ordem: verdade-fonte → CI → hardening → template → cortes → cobertura → backlog.
2. **Abrir PRs por fase** quando o dono confirmar push (branches empilhadas até lá).

## Backlog priorizado (revisto 2026-07-09)

| # | Feature | Esforço | Status |
|---|---------|---------|--------|
| 008 | `kb stats` (dashboard Rich) | ~3h | SPEC draft — Task 11 do plano |
| 009 | `kb diff` (git diff formatado) | ~2h | SPEC draft — Task 12 do plano |
| 010 | multi-vault-foundation | SPEC | Task 13 do plano (só SPEC, HITL) |

### Ondas seguintes (sem mudança desde 2026-04-22)

| # | Feature | Esforço | Bloqueio |
|---|---------|---------|----------|
| — | `kb watch` (compile automático via watchdog) | ~4h | idéia — sem SPEC |
| — | ingest DOCX | ~3h | idéia — sem SPEC |
| 011 | `kb export` (HTML/PDF/EPUB) | ~6-8h | nenhum |
| 012 | MCP Server | ~8-12h + ADR | expor claims/retrieval |
| 013 | ingest RSS/Atom | ~4h | hook `on_schedule` |
| 014 | ingest CSV/TSV | ~2h | valor limitado |

## Médio prazo (P2 herdado)

- Validar `compile_many()` contra provider real com `--workers 4`
- Refinar guardrail de credenciais (falso positivo em nomes de variável)
- Embeddings + RAG híbrido — reavaliar quando wiki > ~200 artigos
- Débitos deferidos do plano: split de `book_import_core.py`, extração de lógica do `cli.py`, unificar slugify, coluna `savings_pct` órfã

## Bloqueadores

Nenhum. Baseline verde: 327/327 testes, ruff clean.
