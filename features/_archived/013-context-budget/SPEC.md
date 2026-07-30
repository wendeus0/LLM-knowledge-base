---
title: Context budget — cap por artigo + perfis de retrieval (fast/deep/paper/article)
epic: qa
status: done
pr:
---

# Context budget — cap por artigo + perfis de retrieval

## Objetivo

Hoje o QA injeta os artigos recuperados **inteiros** no prompt (top_k=5, `router.py`), gerando prompts de 8–10k tokens que levam ~4min de prompt processing no modelo local (M5 base, 33-39 tok/s) — ~5min por pergunta. O sistema deve limitar o contexto por artigo (cap em fronteira de parágrafo) e oferecer perfis de retrieval por operação, levando o QA interativo para ~1,5–2min sem sacrificar o modo de estudo profundo nem os futuros módulos paper/artigo.

Base: análise do vault real (2.059 artigos; mediana 1.433 chars, p75 6.449) e plano aprovado em 2026-07-15 (`~/.claude/plans/vamos-tentar-ajustar-primeiro-cheeky-fern.md`).

## Requisitos funcionais

- [x] RF-01: artigo injetado no contexto do QA é limitado a `doc_chars` caracteres (default 4.000), com corte em fronteira de parágrafo e marcador visível de truncamento; artigo menor que o cap passa intacto
- [x] RF-02: o cap se aplica a TODOS os documentos do contexto — seeds do retrieval, extras do traversal e rota raw
- [x] RF-03: perfis de retrieval nomeados com parâmetros próprios: `fast` (top_k 3, doc_chars 4.000, traversal budget 1.500), `deep` (top_k 5, doc_chars 8.000, budget 4.000), `paper` (top_k 3, doc_chars 4.000, sem traversal), `article` (top_k 5, doc_chars 8.000, traversal on)
- [x] RF-04: `kb qa` usa o perfil `fast` por default; `kb qa --deep` usa o perfil `deep`
- [x] RF-05: `kb qa --top-k N` sobrepõe o top_k do perfil ativo (override manual)
- [x] RF-06: `doc_chars` configurável por env (`KB_QA_DOC_CHARS`) — override global que vale para qualquer perfil
- [x] RF-07: sem `KB_DATA_DIR` exportado, a engine encontra o vault do dono via `.env` local (gitignored) — o comando não cai mais silenciosamente no diretório do repo

## Requisitos técnicos

- Tabela `RETRIEVAL_PROFILES` única em `kb/config.py`; `router.py`/`qa.py` recebem o perfil resolvido (sem hardcode espalhado)
- Corte em `\n\n` mais próximo abaixo do cap; marcador `\n\n[... truncado]`; nunca corta no meio de frase
- Perfis `paper`/`article` são consumidos pelos futuros módulos de autoria — nesta fatia só existem na tabela e são testados unitariamente
- `.env` local com `KB_DATA_DIR` (dotenv já é carregado por `kb/config.py`); permanece fora do versionamento (`.gitignore` já cobre `.env`)
- Experimento operacional fora do código do kb: medir `--ubatch-size` 512/1024/2048 no `start-bonsai-server.sh` com prompt fixo e fixar o melhor valor (registrado no REPORT)

## Mudanças de API/CLI

- `kb qa`: novas flags `--deep` e `--top-k N`; comportamento default muda (perfil fast, top_k 3 + cap) — mais rápido, contexto menor
- Novas env vars: `KB_QA_DOC_CHARS`
- Nenhuma mudança em `search`, `index`, `compile`

## Testes

- Unit (router/config): cap corta em fronteira de parágrafo com marcador; artigo < cap intacto; cap aplicado a seeds + traversal extras + rota raw; perfis retornam os parâmetros da tabela; env override de doc_chars
- Integration (CLI): `kb qa` default usa top_k 3 (observável pelo nº de docs no contexto via mock do chat); `--deep` usa 5; `--top-k 2` sobrepõe
- Manual: as 3 perguntas de referência (bounded context, cardinalidade, bulkhead) em fast e deep, medindo tempo total e `prompt eval time` no log do servidor

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4–6h |
| Bloqueador | não |
| Risk | baixa (comportamento default do qa muda — mitigado por --deep/--top-k e cap generoso) |

## Dependências

- Feature 012 entregue (retrieval híbrido) — os perfis parametrizam o que ela recupera

## Notas

**Fora de escopo (frentes sequenciadas no plano aprovado):**
- Chunking + re-rank + sumários-como-sinal-de-retrieval (SPEC própria, evolução da 012)
- `kb bench` + golden set (feature 014; gate da decisão Bonsai 8B)
- Investigação tensor API → PR ao fork PrismML
- DSpark, streaming, fila assíncrona

**Casos de erro:**
- Artigo sem `\n\n` abaixo do cap (parágrafo gigante) → corte duro no cap com o mesmo marcador (nunca excede)
- Perfil desconhecido solicitado programaticamente → erro claro listando os perfis válidos
- `--top-k 0` ou negativo → erro de validação do CLI

**Open questions:**
- (nenhuma)
