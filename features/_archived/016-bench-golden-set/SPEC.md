---
title: kb bench — medir retrieval contra um golden set
epic: search
status: done
pr:
---

# kb bench — medir retrieval contra um golden set

## Objetivo

Toda decisão de retrieval tomada até aqui foi por argumento, não por medida. Há dois modelos de embedding em disco (`v1.5` e `v2-moe`) sem comparação; 37% dos artigos truncados a 8k chars sem saber quanto isso custa; pesos de RRF herdados sem verificação; e chunking na fila sem baseline contra o qual comparar.

O sistema deve medir a qualidade da recuperação: dado um conjunto de perguntas com os artigos que deveriam aparecer, reportar **recall@k** e **MRR** por configuração, de forma reproduzível. Sem isso, "melhorou" é opinião.

Fatia 3 da Fase 1 do roadmap. É o item 1 dos próximos passos do REPORT de 013 e pré-requisito honesto da 017 (chunking).

## Requisitos funcionais

- [x] RF-01: `kb bench` executa os casos de um golden set e reporta recall@k e MRR agregados, mais a lista de casos que falharam
- [x] RF-02: golden set em arquivo versionável no vault, com formato simples: pergunta + lista de artigos esperados (por slug)
- [x] RF-03: `kb bench --mode lexical|hybrid` mede a mesma bateria em configurações diferentes, permitindo comparação direta
- [x] RF-04: `kb bench --seed` gera um golden set inicial a partir do próprio corpus (título do artigo como pergunta, o artigo como resposta esperada), sem chamar LLM — baseline determinística e ponto de partida para curadoria
- [x] RF-05: `kb bench --k N` define o corte do recall (default 5)
- [x] RF-06: golden set ausente produz mensagem que ensina a criar (`--seed`), não stack trace
- [x] RF-07: caso cujo artigo esperado não existe mais no corpus é reportado como caso inválido, separado das falhas de recuperação — golden set apodrece junto com a wiki
- [x] RF-08: `--json` emite o resultado em formato parseável, para comparação entre execuções

## Requisitos técnicos

- Golden set em JSON, em `kb_state/bench/golden.json` — mesma pasta de estado do vault, versionável junto do corpus
- Métricas: recall@k (proporção de casos em que ao menos um esperado aparece no top-k) e MRR (média do inverso da posição do primeiro acerto)
- Reusa `kb.search.search` com o `mode` já existente; nenhuma lógica de busca nova
- Execução determinística para `--mode lexical`; `hybrid` depende do servidor de embeddings e reporta isso no cabeçalho do resultado
- Sem dependência nova

## Mudanças de API/CLI

- Novo comando `kb bench [--mode] [--k N] [--json] [--seed [--limit N]]`
- Novo artefato: `kb_state/bench/golden.json`

## Testes

- Unit: cálculo de recall@k e MRR com rankings trabalhados à mão (acerto na 1ª, na k-ésima, fora do corte, múltiplos esperados); classificação de caso inválido (artigo inexistente); leitura de golden set ausente/corrompido
- Integration: `bench` sobre corpus de teste com resultado conhecido; `--seed` gerando casos a partir dos títulos; `--mode lexical` e `hybrid` produzindo relatórios distintos; `--json` parseável
- Manual: `kb bench --seed` no vault real seguido de `kb bench --mode lexical` e `--mode hybrid`, comparando os números

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4–6h |
| Bloqueador | não (mas bloqueia decisões de 017 em diante) |
| Risk | baixa (read-only sobre o corpus; não altera índice nem artigos) |

## Dependências

- Feature 012 (canal semântico) para o modo `hybrid`

## Notas

**Fora de escopo:**
- Gerar perguntas por LLM a partir dos artigos (candidato a fatia futura; `--seed` cobre o baseline sem custo)
- Comparar modelos de embedding automaticamente (o comando mede uma configuração por execução; a comparação é o operador rodando duas vezes)
- Métricas de qualidade da resposta gerada (isto mede recuperação, não geração)
- Regressão automática em CI

**Casos de erro:**
- Golden set ausente → orienta `--seed`
- Golden set com JSON inválido → erro claro apontando o arquivo
- Servidor de embeddings fora no modo `hybrid` → o resultado sai, com aviso de que o canal semântico degradou (herdado da 014); o cabeçalho registra isso para não confundir a comparação

**Open questions:**
- (nenhuma)
