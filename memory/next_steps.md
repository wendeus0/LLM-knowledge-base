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

4. **Restringir a saída do rerank:** pedir os N mais relevantes em vez de ordenar 20. É o que resta depois da 022 provar que sampling corrige omissão mas não alucinação de índice. Gate: `kb bench --rerank 20` contra `recall@5 = 0,467 / MRR = 0,343`.
5. **Índice lexical persistente.** `_iter_docs` relê os 1.033 arquivos por query (~3s); é o gargalo de qualquer medição agora que o rerank tem cache.
6. **Verificação contínua do provider durante o lote.** O `preflight` cobre só o início; duas medições foram perdidas por falha no meio.

### P3 — condicionados

7. **Expandir o golden além de 152 casos** se algum experimento futuro tiver delta esperado abaixo de ~4pp.
8. **`ik_llama.cpp` com `--fit` e KV cache q4_0** para viabilizar um 35B na VM — reabriria o teste de compressão. Ressalva: memory pinning da referência é CUDA, a VM é AMD/ROCm.
9. **Revisar `expected` do golden** onde há artigos irmãos igualmente válidos; parte das falhas restantes é erro de medida.
10. **Quantizar ou reverter o chunking** se os 148 MB de índice incomodarem — a 017 não comprovou ganho de recall.

## 2026-08-01

### P1 — decisão do usuário antes de tudo

0. **Mergear ou revisar #59 e #60.** O #59 trava as decisões da política de corpus (o ADR-0018 não existe em `main`, e a SPEC da 023 precisou recuperá-lo do histórico git). O #60 carrega protótipo + especificação da 023.

### P1 — se a 023 seguir

1. **`test-design`** — não `test-red`. Duas condições binárias de risco no PLAN. Testes de contrato HTTP (`GET /v1/models`, `POST /v1/nli`) e de estabilidade do JSON são obrigatórios antes do GREEN.
2. **Provisionar o serviço NLI local em `:1235`.** Porta verificada livre. `torch`/`transformers` ficam fora do `pyproject` por decisão de arquitetura — o serviço é separado, como já é o de embeddings.
3. **Coletar os 12 pares mínimos do holdout** e congelá-los antes de qualquer recalibração. Sem isso não há aceite de desempenho, só testes de contrato.

### P2 — herdado

4. Estágio 1 (cobertura) espera o reagrupamento por tema do ticket 006.
5. Achados F-03/F-06/F-08 da auditoria de segurança seguem abertos no `PENDING_LOG.md`.
