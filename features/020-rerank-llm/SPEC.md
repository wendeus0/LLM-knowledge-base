---
title: Rerank do top-N por LLM
epic: search
status: done
pr:
---

# Rerank do top-N por LLM

## Objetivo

O diagnóstico da 016 e da 017 é consistente: **o artigo certo costuma ser recuperado e mal ordenado.** Com o golden de 152 casos, `recall@5 = 0,414` contra `recall@20 = 0,720` — 30 pontos de recall já estão dentro do top-20, esperando ordenação. Nenhuma mudança de índice atacou isso; chunking e expansão mexeram em quem é recuperado, não em como é ordenado.

O sistema deve, opcionalmente, reordenar os N primeiros candidatos com o LLM, que lê a pergunta e os trechos e julga relevância — algo que cosseno e BM25 não fazem.

Latência foi liberada como restrição: o objetivo declarado é o melhor retorno de artigos possível.

Baseline a superar: **recall@5 = 0,414 / MRR = 0,242** (152 casos). Teto teórico do rerank: 0,720, o recall@20 atual.

## Requisitos funcionais

- [x] RF-01: `rerank(question, candidates)` devolve os candidatos reordenados por julgamento do LLM
- [x] RF-02: o rerank recebe título e trecho de cada candidato — julgar por slug seria adivinhação
- [x] RF-03: falha do LLM, resposta malformada ou candidato inventado degradam para a ordem original, com aviso
- [x] RF-04: candidatos que o LLM omitir da resposta permanecem depois dos ranqueados, na ordem original — nenhum resultado desaparece por omissão do modelo
- [x] RF-05: opt-in por `--rerank N` em `search` e `bench`, onde N é a profundidade a reordenar
- [x] RF-06: cache por (pergunta, conjunto de candidatos, modelo)

## Requisitos técnicos

- Reusa `kb.client.chat`; sem modelo dedicado de rerank e sem dependência nova
- O prompt pede uma lista ordenada de índices, não texto livre — parsing tolerante a ruído do modelo
- Trecho por candidato limitado, para o prompt de N=20 caber com folga
- Rerank ocorre **depois** da fusão RRF, sobre o resultado final; não substitui nenhum canal
- Nenhuma chamada de rede em teste

## Mudanças de API/CLI

- Novo módulo `kb/rerank.py`
- `kb search --rerank N`, `kb bench --rerank N`

## Testes

- Unit: parsing da resposta (lista limpa, com ruído, com índice inválido, vazia); preservação de candidatos omitidos; degradação em falha do LLM; cache
- Integration: `search --rerank` alterando a ordem com LLM mockado; sem a flag, ordem intocada
- Manual: `kb bench --rerank 20` contra a baseline 0,414/0,242

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4–6h |
| Bloqueador | não |
| Risk | baixa (opt-in, pós-processamento; a busca continua igual sem a flag) |

## Dependências

- 016 (bench), 019 (golden de 152 casos para medir com resolução)

## Notas

**Fora de escopo:**
- Reranker dedicado (cross-encoder) — exigiria baixar modelo; o LLM local já está disponível
- Rerank de chunks em vez de artigos
- Ligar por padrão antes da medição justificar

**Casos de erro:**
- LLM devolve índice fora do intervalo → ignorado, sem quebrar
- LLM devolve menos itens que o pedido → o restante mantém ordem original
- LLM fora do ar → ordem original com aviso

**Open questions:**
- (nenhuma)
