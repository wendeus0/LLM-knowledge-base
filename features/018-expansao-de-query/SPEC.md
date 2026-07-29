---
title: Expansão de query — ponte entre pergunta conceitual e termo técnico
epic: search
status: done
pr:
---

# Expansão de query — ponte entre pergunta conceitual e termo técnico

## Objetivo

A investigação da 017 diagnosticou a causa real das falhas de recuperação, e ela não é granularidade nem ranking: **o embedding não faz a travessia de conceito para termo técnico**. *"achar o trajeto mais barato entre dois pontos de uma rede"* devolve `pontos-de-integracao` — "rede" foi lido como rede de sistemas, não grafo. *"período combinado em que é permitido mexer em produção"* não encontra `a-janela-de-mudanca`.

Quem pergunta raramente conhece o termo que o artigo usa — é justamente por isso que está perguntando. O sistema deve reescrever a pergunta no vocabulário provável do corpus **antes** de buscar, usando o LLM local já configurado.

Baseline a superar (golden curado, 50 casos, índice com chunking): **recall@5 = 0,440 / MRR = 0,246**.

## Requisitos funcionais

- [x] RF-01: `expand_query` reescreve a pergunta acrescentando termos técnicos prováveis, sem descartar os termos originais
- [x] RF-02: duas estratégias selecionáveis — `terms` (acrescenta vocabulário técnico) e `hyde` (gera um trecho hipotético de artigo que responderia à pergunta, e busca com ele)
- [x] RF-03: expansão é **opt-in**; sem ela, `search`/`qa` mantêm o comportamento atual byte a byte
- [x] RF-04: resultado da expansão é cacheado por (pergunta, estratégia, modelo) — a mesma pergunta não paga duas vezes
- [x] RF-05: falha do LLM não quebra a busca: cai para a query original com aviso, como toda degradação do projeto
- [x] RF-06: `kb bench --expand terms|hyde` mede o efeito contra o mesmo golden
- [x] RF-07: `kb search` e `kb qa` aceitam `--expand` — **parcial:** entregue em `search` e `bench`; não ligado no `qa`, porque 10s por pergunta anularia o ganho de latência da 013 (ver REPORT)

## Requisitos técnicos

- Usa `kb.client.chat` com o `KB_MODEL` já configurado — sem provedor novo, sem dependência nova
- Cache em `kb_state/query_expansion.json`, chaveado por hash de (pergunta, estratégia, modelo)
- Prompt curto e com teto de tokens: o custo por query precisa ser baixo o bastante para caber no caminho interativo
- A query expandida entra **apenas** no canal semântico; os canais lexicais continuam usando a pergunta original, para não degradar o casamento exato que hoje funciona
- Nenhuma chamada de rede em teste — `chat` é monkeypatchado, como nos demais módulos

## Mudanças de API/CLI

- Novo módulo `kb/query_expansion.py`
- `kb search`/`kb qa`: flag `--expand [terms|hyde]`
- `kb bench`: flag `--expand [terms|hyde]`
- Novo artefato: `kb_state/query_expansion.json`

## Testes

- Unit: montagem do prompt por estratégia; preservação dos termos originais em `terms`; cache (hit, miss, invalidação por modelo diferente); degradação silenciosa quando `chat` levanta; resposta vazia do LLM tratada como falha
- Integration: `search --expand` consultando o canal semântico com a query expandida e os lexicais com a original; `bench --expand` produzindo relatório; sem `--expand`, resultado idêntico ao atual
- Manual: `kb bench --expand terms` e `--expand hyde` contra a baseline 0,440/0,246

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4–6h |
| Bloqueador | não |
| Risk | baixa (opt-in; caminho padrão intocado) |

## Dependências

- Feature 016 (bench) para medir; 012 (canal semântico) para ter o que expandir

## Notas

**Fora de escopo:**
- Expansão por dicionário/tesauro estático (o LLM local já está disponível e é mais flexível)
- Reescrita da pergunta para o LLM de resposta (isto afeta recuperação, não geração)
- Expansão automática por padrão — só depois de a medição justificar

**Casos de erro:**
- LLM fora do ar ou lento → timeout, aviso, query original
- Resposta do LLM vazia ou sem conteúdo útil → query original
- Cache corrompido → ignorado e reescrito, sem quebrar a busca

**Hipótese sob teste:** se a causa diagnosticada na 017 estiver certa, `--expand` deve recuperar boa parte dos 28 casos que falham hoje, especialmente os que usam paráfrase conceitual. Se o recall não mover, a hipótese estava errada e o próximo experimento muda de direção.

**Open questions:**
- (nenhuma)
