---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **Escolher frente principal**
   - `llm-wiki-v2-foundation` (PLAN_READY → test-red) — maior impacto, rework da engine
   - `ingest-url` (WORKFLOW_OK → git-flow-manager) — commit rápido
   - `006-kb-archive` (WORKFLOW_OK → git-flow-manager) — commit rápido

2. **Decidir sobre kb/audit.py**
   - Integrar em feature existente, criar feature nova, ou descartar

3. **Limpeza de features órfãs**
   - `features/001-wikilink-traversal/` e diretórios concluídos sem .state

## Médio prazo

4. **[P2] Validar `compile_many()` contra provider real**
   - Usar pequeno lote com `--workers 4`
   - Confirmar ausência de corrupção em `kb_state/` e `_index.md`

5. **[P2] Consolidar ergonomia do Obsidian**
   - Base operacional; sem bloqueador técnico

6. **[P2] Refinar guardrail de credenciais**
   - Falso positivo em nomes de variável em blocos de código

7. **[P2] Completar separação engine vs. corpus**
   - TOPICS já migrando para runtime taxonomy (ADR-0015)
   - Neutralizar referências históricas restantes

8. **[P2] Embeddings + RAG híbrido**
   - Reavaliar quando wiki ultrapassar ~200 artigos

## Backlog (ideias do usuário)

9. MCP Server para integração externa
10. Mais formatos de importação
11. kb export (wiki → formato portátil)

## Bloqueadores

- Nenhum. Baseline verde: 308/308 testes, 92% cobertura, ruff clean, main alinhada.
