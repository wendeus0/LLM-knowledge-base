# ADR 0017 — Retrieval híbrido com rerank por LLM, decidido por medição

- **Status:** Aceito
- **Data:** 2026-07-30
- **Supera:** [ADR 0004](0004-keyword-search-strategy.md)
- **Fecha o gatilho de revisão de:** [ADR 0013](0013-claim-centric-lifecycle-and-hybrid-retrieval-foundation.md)

## Contexto

O ADR-0004 (2026-04-04) adotou busca por keywords e rejeitou explicitamente vector search, listando "necessidade de busca semântica" como o gatilho que exigiria revisitar a decisão. O ADR-0013 (2026-04-12) declarou o eixo semântico como parte da fundação e deixou aberto "avaliar custo/benefício ao ativar embeddings em produção".

Os dois gatilhos dispararam:

- o corpus passou de ~475 artigos previstos para **1.033 artigos e 4,2M palavras**, acima do teto de ~500 que o `SDD.md` fixava para dispensar RAG;
- perguntas conceituais que não repetem os termos do artigo alvo falhavam de forma sistemática, que é precisamente a limitação que o ADR-0004 antecipou.

O que não existia em abril era **instrumento**. Sem medição, trocar a estratégia de busca seria substituir uma intuição por outra.

## Decisão

Adotar retrieval híbrido em quatro canais fundidos por RRF — keyword, densidade, BM25 e semântico por embeddings — com rerank opcional por LLM sobre os primeiros candidatos.

Cada mudança foi aceita ou rejeitada por medição contra um golden set de 152 casos sobre o corpus real (`kb bench`), nunca por plausibilidade:

| Configuração | recall@5 | MRR |
|---|---|---|
| lexical (keyword + densidade + BM25) | 0,230 | 0,127 |
| + canal semântico | 0,414 | 0,242 |
| + rerank dos 20 primeiros @ temp 0,8 | 0,467 | 0,299 |
| **+ rerank dos 20 primeiros @ temp 0** | **0,467** | **0,343** |

Parâmetros fixados:

1. **Sem vector store.** Brute-force em memória sobre `kb_state/embeddings.json` basta neste volume — mesma razão pela qual o ADR-0004 rejeitou infraestrutura de busca dedicada. FAISS/lancedb/sqlite-vec permanecem fora.
2. **Embeddings locais** (`nomic-embed-text-v2-moe` via LM Studio) — preserva a propriedade offline que o ADR-0004 valorizava; nenhum conteúdo do corpus vai a provider externo para indexar.
3. **Rerank a temperatura 0**, provider dedicado (`KB_RERANK_MODEL`, `KB_RERANK_BASE_URL`), separado do modelo de QA.
4. **Degradação com aviso.** Servidor de embeddings ausente cai para lexical, mas nunca em silêncio.

## Consequências

### Positivas

- recall@5 dobrou e MRR quase triplicou sobre a estratégia do ADR-0004
- toda decisão futura de retrieval tem instrumento: `kb bench` mede antes de adotar
- três hipóteses plausíveis foram **rejeitadas por medição**, e ficam registradas para não serem retentadas: chunking por seção (+1 caso em 50, MRR pior), expansão de query por termos (ganho zero), e trocar o modelo de rerank por um 13× mais rápido (0,388 — pior que não reordenar)

### Negativas

- `kb qa` depende de dois servidores locais para operar em qualidade plena, mitigado por LaunchAgents e degradação explícita
- rerank custa uma chamada de LLM: ~11s por pergunta no `qa`, ~34s no `search`, razão pela qual é opt-in no `search`
- o índice de embeddings é um artefato derivado de 148 MB que precisa acompanhar o corpus (`kb index build`, refresh automático em compile/heal)

### Neutras

- o canal lexical não foi removido: ele continua respondendo por 3 dos 4 rankings fundidos, e o ADR-0004 permanece a explicação de por que ele é como é

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Manter keyword-only (ADR-0004) | Medido: `recall@5` 0,230 contra 0,467. O gatilho de revisão do próprio ADR disparou |
| Vector store dedicado | Volume não justifica; brute-force resolve e evita segunda fonte de verdade |
| Embeddings via API externa | Quebraria a propriedade offline e enviaria o corpus a terceiros |
| Substituir o lexical pelo semântico | O híbrido supera cada canal isolado; o RRF existe para isso |
| Rerank sempre ligado no `search` | Latência de 2,7s para 36,7s numa operação exploratória |

## Gatilhos de revisão

- corpus acima de ~5.000 artigos, onde brute-force em memória deixa de ser barato
- `recall@20` (hoje 0,720) virar o gargalo em vez da ordenação
- modelo de rerank que elimine alucinação de índice — hoje o modo de falha dominante, e o único não corrigível por configuração
