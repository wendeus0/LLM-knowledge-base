---
name: Next Steps
description: Próximos passos priorizados
type: project
---

## Atualizado: 2026-07-31

### P0 — a mais urgente do sprint

0. **Proteger o que não é reconstruível** (ticket 001 do map, frontier). O golden de 152 casos (`~/vault/kb_state/bench/golden.json`) e as **869 fontes de `library/` (185 MB, fora do git)** sustentam toda decisão sobre o corpus. O ticket 006 discute recompilar; sem o material bruto, essa opção deixa de existir. Barato e destrava o resto do map.

### P1 — decisão central do map, agora destravada

1. **Ticket 004 — a wiki é produto ou insumo?** Destravou com 002 e 003 entregues. Decide se o compile precisa de gate de profundidade, se a definição de artigo robusto de `011/DOMAIN.md` volta, e se a interface do 007 é leitor ou front do `qa`. As outras decisões derivam desta.

### P1 — baratos e destravam o resto

1. ~~Decidir onde o golden set mora~~ — absorvido pelo item 0 acima, que amplia o escopo para `library/`.

~~2. Documentar a config vencedora no `.env.example`~~ — feito em 2026-07-30.
~~3. Push da branch~~ — mergeada em `main` (`f694190`) e publicada.

### P2 — próximo ganho de retrieval

4. ~~**Restringir a saída do rerank:** pedir os N mais relevantes em vez de ordenar 20~~ — **NEGATIVO MEDIDO (2026-07-31)**. Implementado e medido em `feat/rerank-top-n` (não mergeado). Zerou os índices fora da faixa, que era o alvo, mas **recall@5 caiu de 0,526 para 0,493** (−5 acertos em 152) porque o modelo devolve menos do que se pede: cobertura 0,91, seis omissões severas. MRR subiu (0,352 → 0,364) — acerta em posição melhor, erra mais vezes. Medição limpa (`failed: 0`, `degraded: false`). Reabrir só se o critério do projeto virar MRR, ou com reranker que não omita.
5. **Índice lexical persistente.** `_iter_docs` relê os 1.033 arquivos por query (~3s); é o gargalo de qualquer medição agora que o rerank tem cache.
6. **Verificação contínua do provider durante o lote.** O `preflight` cobre só o início; duas medições foram perdidas por falha no meio.

### P3 — condicionados

7. **Expandir o golden além de 152 casos** se algum experimento futuro tiver delta esperado abaixo de ~4pp.
8. **`ik_llama.cpp` com `--fit` e KV cache q4_0** para viabilizar um 35B na VM — reabriria o teste de compressão. Ressalva: memory pinning da referência é CUDA, a VM é AMD/ROCm.
9. **Revisar `expected` do golden** onde há artigos irmãos igualmente válidos; parte das falhas restantes é erro de medida.
10. **Quantizar ou reverter o chunking** se os 148 MB de índice incomodarem — a 017 não comprovou ganho de recall.
