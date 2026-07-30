---
title: Golden set em escala — geração de perguntas por LLM
epic: search
status: done
pr:
---

# Golden set em escala — geração de perguntas por LLM

## Objetivo

Três experimentos consecutivos de retrieval (chunking, expansão por termos, HyDE) produziram deltas de 1 a 2 casos num golden de 50. Com essa amostra, o erro padrão é da ordem de 7 pontos percentuais — **o instrumento não distingue mais ganho real de ruído**, e cada conclusão fica frágil.

O sistema deve gerar casos de avaliação em escala: para um artigo amostrado do corpus, o LLM escreve a pergunta que um usuário faria **sem conhecer o vocabulário do artigo** — que é a condição em que o retrieval realmente falha, conforme medido na 017.

O golden curado à mão (50 casos) permanece como referência de qualidade; os gerados ampliam a amostra.

## Requisitos funcionais

- [x] RF-01: `kb bench --seed-questions N` amostra N artigos do corpus e gera, para cada um, uma pergunta em linguagem de usuário
- [x] RF-02: a pergunta gerada evita os termos técnicos do título e do corpo — o prompt exige paráfrase conceitual, que é onde o retrieval falha
- [x] RF-03: casos gerados são marcados com `source: generated`; os curados à mão mantêm `source: curated` — o relatório pode separar as duas populações
- [x] RF-04: geração é incremental: rodar de novo acrescenta casos novos sem duplicar artigos já cobertos
- [x] RF-05: artigo cuja pergunta gerada contenha o título quase literal é descartado — seria caso trivial, do tipo que inflava a medição do seed original
- [x] RF-06: `kb bench` reporta as métricas separadas por população (curated, generated, total)

## Requisitos técnicos

- Reusa `kb.client.chat` e o formato de golden já existente
- Geração é lenta por natureza (uma chamada por artigo); o comando deve ser retomável e nunca perder o que já gerou
- Semente de amostragem fixa para reprodutibilidade
- Sem dependência nova

## Mudanças de API/CLI

- `kb bench --seed-questions N [--sample-seed S]`
- Campo `source` em cada caso do golden

## Testes

- Unit: descarte de pergunta que repete o título; marcação de `source`; amostragem determinística por semente; incrementalidade (não regerar artigo já coberto)
- Integration (chat mockado): geração de N casos; segunda execução acrescenta sem duplicar; métricas separadas por população
- Manual: gerar ~100 casos no vault real, revisar amostra e re-medir a baseline

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 3–4h |
| Bloqueador | **sim** — bloqueia conclusões dos próximos experimentos de retrieval |
| Risk | baixa (só escreve golden; não toca índice nem corpus) |

## Dependências

- Feature 016 (bench e formato de golden)

## Notas

**Fora de escopo:**
- Validar automaticamente se a pergunta gerada é boa (a revisão é humana, por amostra)
- Gerar múltiplas perguntas por artigo
- Substituir os 50 casos curados

**Viés conhecido e aceito:** a pergunta é derivada do artigo, então o caso nasce com a garantia de ter resposta — diferente do uso real, em que boa parte das perguntas não tem artigo correspondente. Isso mede recuperação, não cobertura do corpus, e é a mesma limitação do golden curado.

**Open questions:**
- (nenhuma)
