# REPORT — 018-expansao-de-query

**Data:** 2026-07-29
**Status:** `DONE_WITH_CONCERNS` — hipótese da 017 confirmada; ganho real mas modesto, e caro demais para ser default.
**Ciclo:** SPEC → TASKS → RED (13 testes) → GREEN → medição das duas estratégias no vault real

## O que mudou

- **`kb/query_expansion.py` (novo):** `expand_query(query, strategy)` com duas estratégias — `terms` (acrescenta vocabulário técnico preservando a pergunta) e `hyde` (gera o parágrafo de um verbete hipotético e busca com ele). Cache em `kb_state/query_expansion.json` chaveado por (pergunta, estratégia, modelo). Falha do LLM ou resposta vazia devolve a pergunta original com aviso.
- **`kb/search.py`:** parâmetro `expand`, aplicado **apenas** ao canal semântico — os lexicais funcionam por casamento de termo e seriam diluídos por vocabulário gerado.
- **`kb/bench.py` e `kb/cli.py`:** `--expand` em `bench` e `search`; `search` também ganhou `--mode`, que só existia via API.

## Validação

- 13 testes novos (10 de expansão/cache, 3 de integração com `search`), nascidos RED por `AssertionError`. Suíte: **541 passed**, 93%, ruff limpo.
- Dois testes existentes atualizados para o novo contrato de kwargs de `search`.

### Medição (golden curado, 50 casos, índice com chunking)

| Configuração | recall@5 | MRR | acertos |
|---|---|---|---|
| sem expansão | 0,440 | 0,246 | 22/50 |
| `--expand terms` | 0,440 | 0,232 | 22/50 |
| **`--expand hyde`** | **0,480** | **0,278** | **24/50** |

**HyDE é o primeiro experimento desta sequência que melhora as duas métricas simultaneamente.** `terms` não moveu o recall e piorou o MRR — acrescentar palavras-chave à pergunta dilui o vetor sem reposicioná-lo.

### A hipótese da 017 se confirmou

Caso a caso, HyDE ganhou 4 e perdeu 2. Os quatro ganhos são exatamente paráfrases conceituais sem termo técnico:

| Pergunta | Termo que faltava |
|---|---|
| dividir o sistema em peças substituíveis com fronteira bem definida | componentes |
| guardar o histórico de mudanças em vez do estado atual da entidade | event sourcing |
| quando vale escolher a melhor opção local em vez de resolver subproblemas | algoritmo guloso |
| quanto a qualidade dos exemplos pesa em relação à escolha do algoritmo | dados de treinamento |

O mecanismo funciona: comparar documento hipotético com documento real é mais eficaz que comparar pergunta com documento. Exemplo da expansão gerada para *"achar o trajeto mais barato entre dois pontos de uma rede"*: *"A função mais relevante é o algoritmo de Dijkstra, que calcula o caminho de menor custo entre um nó inicial e todos os outros em uma rede ponderada não negativa."*

## Riscos / dívida

- **O ganho é modesto e não é estatisticamente forte.** +2 casos líquidos em 50; com esse tamanho de amostra, o erro padrão é da ordem de 7 pontos. O sinal é consistente (ganha em recall e MRR, e os casos ganhos batem com o mecanismo previsto), mas confirmar exige golden maior.
- **Custo proibitivo para uso interativo:** ~10s por query com `bonsai-27b-1bit` local. O bench de 50 casos levou 8m50 na primeira passada. Por isso a expansão é opt-in e **não** foi ligada no `kb qa` — acrescentar 10s a cada pergunta destruiria o ganho de latência que a 013 conquistou.
- **`kb qa --expand` não foi entregue** (RF-07 parcial). A flag existe em `bench` e `search`. Ligar no `qa` só faz sentido com um modelo de expansão rápido.
- **HyDE alucina com confiança.** O documento hipotético pode inventar um assunto que não existe no corpus e puxar o ranking para o lado errado — foi o que aconteceu nos 2 casos perdidos. O cache torna isso reprodutível, o que é bom para depurar e ruim se o erro ficar congelado.

## Próximos passos

1. **Expandir o golden para 100–150 casos.** Três experimentos seguidos (chunking, terms, hyde) produziram diferenças de 1 a 2 casos — abaixo da resolução do instrumento. Sem isso, os próximos experimentos continuam inconclusivos.
2. Medir HyDE com um modelo de expansão mais rápido; se cair para ~1s por query, reconsiderar como default.
3. Revisar o `expected` do golden onde há irmãos válidos — parte dos 26 casos que ainda falham pode ser erro de medida, não de busca.
