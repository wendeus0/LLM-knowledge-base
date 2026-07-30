---
name: Next Steps
description: Próximos passos priorizados
type: project
---

## Atualizado: 2026-07-30

### P1 — baratos e destravam o resto

1. **Documentar a config vencedora no `.env.example`:** rerank com `bonsai-27b-1bit` (`localhost:8081`) e perfil `deterministic`. Sem isso a configuração medida se perde.
2. **Decidir onde o golden set de 152 casos mora.** Hoje em `~/vault/kb_state/bench/golden.json`, num vault não versionado. Diferente do índice, **não é reconstruível** — os 50 casos curados são trabalho manual.
3. **Push e PR** dos 10 commits da branch `feat/semantic-retrieval-foundation` (aguardando pedido explícito do dono).

### P2 — próximo ganho de retrieval

4. **Restringir a saída do rerank:** pedir os N mais relevantes em vez de ordenar 20. É o que resta depois da 022 provar que sampling corrige omissão mas não alucinação de índice. Gate: `kb bench --rerank 20` contra `recall@5 = 0,467 / MRR = 0,343`.
5. **Índice lexical persistente.** `_iter_docs` relê os 1.033 arquivos por query (~3s); é o gargalo de qualquer medição agora que o rerank tem cache.
6. **Verificação contínua do provider durante o lote.** O `preflight` cobre só o início; duas medições foram perdidas por falha no meio.

### P3 — condicionados

7. **Expandir o golden além de 152 casos** se algum experimento futuro tiver delta esperado abaixo de ~4pp.
8. **`ik_llama.cpp` com `--fit` e KV cache q4_0** para viabilizar um 35B na VM — reabriria o teste de compressão. Ressalva: memory pinning da referência é CUDA, a VM é AMD/ROCm.
9. **Revisar `expected` do golden** onde há artigos irmãos igualmente válidos; parte das falhas restantes é erro de medida.
10. **Quantizar ou reverter o chunking** se os 148 MB de índice incomodarem — a 017 não comprovou ganho de recall.
