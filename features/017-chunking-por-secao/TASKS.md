# TASKS — 017-chunking-por-secao

| ID | Task | Depende de | RF | Estado |
|---|---|---|---|---|
| T-01 | `split_sections()` — corpo em (heading, conteúdo), com preâmbulo | — | RF-01 | done |
| T-02 | `build_chunks()` — contexto no texto, agrupa curtas, divide longas | T-01 | RF-02, RF-04, RF-05 | done |
| T-03 | `build_index` grava chunks por artigo, com `format: 2` e incrementalidade por hash | T-02 | RF-01, RF-06 | done |
| T-04 | `load_index` rejeita formato antigo; `semantic_ranking` agrega por máximo | T-03 | RF-03, RF-07 | done |
| T-05 | `index_status` e `index build` reportam chunks | T-03 | RF-08 | done |
| T-06 | Rebuild no vault real + `kb bench` contra a baseline 0,420/0,272 | T-01..T-05 | — | done |

## Ordem

T-01 → T-02 → T-03 → T-04 → T-05 → T-06

## Definição de pronto (por task)

Teste RED nascido antes da implementação, falhando por `AssertionError`; GREEN com a suíte inteira verde; `ruff check kb tests` limpo.

T-06 é o gate da feature: sem ganho medido sobre a baseline, a decisão é reverter, não ajustar até passar.
