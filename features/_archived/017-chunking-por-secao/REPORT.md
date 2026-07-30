# REPORT — 017-chunking-por-secao

**Data:** 2026-07-29
**Status:** `DONE_WITH_CONCERNS` — implementada e medida; **não bateu a baseline**. Mantida por corrigir o truncamento, não por ganho de recall.
**Ciclo:** SPEC → PLAN/TASKS → RED (17 testes) → GREEN → medição no vault real → investigação do resultado negativo

## O que mudou

- **`kb/chunking.py` (novo):** `split_sections` (corpo → seções por `##`, preâmbulo como seção própria, `###` permanece dentro do pai) e `build_chunks` (contexto `título — heading` em cada chunk, agrupamento de seções curtas, divisão de seções longas em fronteira de palavra).
- **`kb/embeddings.py`:** índice passa a guardar um vetor por seção (`format: 2`); `load_index` rejeita o formato antigo em vez de misturar; `semantic_ranking` agrega chunks por **máximo** — soma favoreceria artigo longo por ter mais seções, o viés que a feature existia para corrigir.
- **`kb/cli.py`:** `index status` e `index build` reportam chunks.
- Teste de truncamento da 012 substituído pelo contrato novo: conteúdo acima do limite é dividido, e a soma dos chunks preserva o corpo inteiro.

## Validação

- 17 testes novos (10 de chunking, 7 de índice/agregação), nascidos RED por `AssertionError`. Suíte: **528 passed**, 93%, ruff limpo.
- Corpus real: 1.037 artigos → **8.685 chunks** (8,4 por artigo). Build 4m32 (contra 70s). Índice 17,8 MB → **141 MB**.

### O gate falhou

| Métrica | Baseline (1 vetor/artigo) | Chunking | Δ |
|---|---|---|---|
| recall@5 | 0,420 (21/50) | 0,440 (22/50) | +1 caso |
| MRR@5 | 0,272 | 0,246 | pior |
| recall@10 | 0,520 | 0,520 | — |
| recall@20 | 0,720 | 0,660 | −3 casos |

Comparação caso a caso (baseline medida em worktree no commit anterior, para não comparar código novo com código velho): **ganhou 1, perdeu 0**. Os 28 casos que falhavam continuam falhando, os mesmos.

## Investigação do resultado negativo

**Hipótese 1 — o prefixo de contexto domina chunks curtos, tornando-os indistinguíveis: refutada.** Similaridade mediana intra-artigo 0,732 contra inter-artigo 0,477 (separação +0,255). Os chunks são distintos entre si e os artigos permanecem distinguíveis.

**Hipótese 2 — granularidade era o gargalo: refutada pelos dados.** Mesmos casos falhando, MRR pior.

**O que a inspeção dos casos falhos revelou** foram duas causas que a métrica agregava:

1. **Golden estreito.** Para *"por onde eu começo a estudar projeto e análise de algoritmos"* o sistema devolve `fundamentos-de-algoritmos-e-estruturas-de-dados` e `practical-algorithm-design-sumario` — respostas boas que o `expected` (`03-part-i-foundations`) rejeita. Parte do 0,42 é erro de medida.
2. **Falha de ponte conceito → termo técnico.** *"achar o trajeto mais barato entre dois pontos de uma rede"* devolve `pontos-de-integracao`: "rede" foi lido como rede de sistemas, não grafo. *"período combinado em que é permitido mexer em produção"* não encontra `a-janela-de-mudanca`. As perguntas foram escritas de propósito sem termos técnicos, e o embedding não faz essa travessia.

**Nenhuma mudança de granularidade do índice resolve (2).** É limitação de vocabulário do modelo, e aponta para expansão de query como próximo experimento — não para mais ajuste de índice.

## Decisão

Mantida, com ressalva explícita: **o ganho medido é ruído** (1 caso em 50), e MRR e recall@20 pioraram. O que justifica manter é a correção de um defeito real — 35% do corpus estava invisível por truncamento a 8k, e agora não está. Esse ganho não aparece neste golden porque as 50 perguntas calham de ter resposta na primeira seção dos artigos.

Se o custo de disco ou de build incomodar, reverter é legítimo e o histórico preserva o código.

## Riscos / dívida

- **141 MB de índice** para 36 MB de texto. Quantização de vetores é a saída óbvia se incomodar.
- **Build 4× mais lento.** Incremental continua barato: artigo inalterado não re-embeda nenhum chunk.
- **Índice formato 1 é rejeitado**, não migrado. Quem tiver índice antigo precisa de um `kb index build`. Aceito por ser artefato derivado.
- A latência de busca com 8.685 vetores não foi medida isoladamente; o bench de 50 casos não acusou degradação perceptível, mas `numpy` continua sendo o plano B.

## Próximos passos

1. **Expansão de query** — ataca a causa diagnosticada (conceito → termo técnico), e o mesmo golden serve de gate.
2. Revisar o `expected` do golden onde há artigos irmãos igualmente válidos; a medida atual pune resposta correta.
3. Se o índice de 141 MB incomodar antes disso, quantizar ou reverter.
