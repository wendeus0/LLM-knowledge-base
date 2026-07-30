# REPORT — 020-rerank-llm

**Data:** 2026-07-29
**Status:** `DONE` — maior ganho medido da sequência de retrieval.
**Ciclo:** SPEC → RED (21 testes) → GREEN → instrumentação de omissão → medição em 152 casos

## O que mudou

- **`kb/rerank.py` (novo):** manda pergunta + candidatos (título e trecho) ao LLM e usa a ordem devolvida. Toda a defesa está no parsing — índice fora de faixa, duplicado ou omitido nunca fazem resultado desaparecer: o omitido volta ao fim, na ordem original. Cache por (pergunta, candidatos, modelo).
- **`kb/search.py`:** `rerank_depth` busca mais fundo do que devolve, reordena o topo e corta em `top_k`.
- **`kb/bench.py`, `kb/cli.py`:** `--rerank N` em `bench` e `search`.
- **Instrumentação de omissão:** `parse_order_with_stats` e contadores acumulados (`calls`, `cache_hits`, `failed`, `unparseable`, `severe_omission`, `out_of_range_total`, `duplicates_total`, `coverage`), reportados pelo `bench`.

## Validação

- 21 testes novos (11 de rerank, 10 de instrumentação), nascidos RED. Suíte: **569 passed**, 92%, ruff limpo.

### Resultado (golden de 152 casos, índice com chunking)

| Configuração | recall@5 | MRR | acertos |
|---|---|---|---|
| baseline (hybrid) | 0,414 | 0,242 | 63/152 |
| **rerank 20** | **0,467** | **0,299** | **71/152** |
| — curados (50) | 0,440 → **0,520** | | |
| — gerados (102) | 0,402 → **0,441** | | |

**+5,3 pontos de recall (+13% relativo) e +5,7 de MRR (+24% relativo).** Com n=152 o erro padrão é ~4 pontos: é o primeiro experimento da sequência que supera o ruído, e o ganho aparece nas duas populações. Resultado reproduzido em segunda execução.

Comparação com os anteriores, todos no mesmo instrumento:

| Experimento | Δ recall@5 | Δ MRR |
|---|---|---|
| chunking por seção | +0,02 (ruído) | −0,026 |
| expansão `terms` | 0,000 | −0,014 |
| expansão `hyde` | +0,04 | +0,032 |
| **rerank 20** | **+0,053** | **+0,057** |

### O ganho veio com o modelo entregando 75% do pedido

A instrumentação existe porque o descarte era silencioso. Nas 152 chamadas reais:

| Métrica | Valor |
|---|---|
| Devolveu os 20 índices pedidos | 20% |
| Cobertura média | 75% |
| Omissão severa (<50% dos candidatos) | 26% |
| Devolveu ≤5 índices | 30 chamadas |
| Mediana / mín / máx | 19 / 2 / 20 |

Um quarto das chamadas praticamente não reordenou — o `bonsai-27b-1bit` degrada em saída estruturada longa, que é onde a quantização a 1 bit dói. **O ganho de +5,3 pontos foi obtido nessa condição.** Com um modelo que responda completo, há margem: o teto é `recall@20 = 0,720`, e hoje estamos em 0,467.

## Riscos / dívida

- **Custo:** ~20s por query com o modelo local. Aceitável pela diretriz do dono (qualidade acima de latência), mas inviabiliza uso interativo sem cache quente. O bench de 152 casos leva ~50 min a frio.
- **A busca lexical virou o gargalo do bench**, não o LLM: com cache quente, 152 casos ainda levam 9 min, porque `_iter_docs` relê os 1.033 arquivos a cada query. Índice lexical persistente resolveria.
- **Omissão severa em 26% das chamadas** é dívida de qualidade do modelo, não do código. Um prompt que force saída completa, ou um modelo menos quantizado, é o próximo ajuste natural — e agora é mensurável.
- Rerank não foi ligado no `kb qa`, pela mesma razão da 018.

## Próximos passos

1. Atacar a omissão: prompt que exija as N posições explicitamente, ou modelo de rerank menos comprimido. A instrumentação já mede o efeito.
2. Combinar `--rerank 20 --expand hyde` — os dois ganhos podem ser aditivos, já que atacam etapas diferentes (recuperação vs ordenação).
3. Índice lexical persistente, que agora é o gargalo de qualquer medição.
