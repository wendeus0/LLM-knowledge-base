# PENDING_LOG.md

Pendências e decisões abertas.

| Prioridade | Item | Status | Data |
|------------|------|--------|------|
| P0 | Configurar API key + modelo | ✓ RESOLVIDO | 2026-04-03 |
| P1 | Implementar testes (tests/) | Pendente | 2026-04-03 |
| P2 | Integração Obsidian | Pendente | 2026-04-03 |
| P2 | Embeddings + RAG | Pendente (futuro) | 2026-04-03 |

## P0 (Bloqueadores)

✓ **RESOLVIDO: Modelo LLM (kimi-k2.5)**
- Solução: usar nome do modelo sem prefixo: `kimi-k2.5` (não `opencode-go/kimi-k2.5`)
- Modelo suportado: Kimi K2.5, Minimax 2.7, GLM-5
- Status: Pipeline completo testado e funcionando

## P1 (Importante)

**Testes (tests/)**
- Estrutura pronta, mas sem testes
- Cobrir: compile, qa, search, heal, lint
- Gateway: 70%+ coverage unit + integração

## P2 (Nice-to-have)

**Obsidian integration**
- Wiki já é Obsidian-compatible (markdown + wikilinks)
- Futuro: plugin Obsidian que chama `kb` via CLI

**Embeddings + RAG**
- Atual: TF-IDF simples funciona até ~100 artigos
- Quando escalar: adicionar embeddings + FAISS ou similar
- Não bloqueia — milestone futuro
