# TASKS — 018-expansao-de-query

| ID | Task | Depende de | RF | Estado |
|---|---|---|---|---|
| T-01 | `expand_query()` — estratégias `terms` e `hyde`, degradação para a original | — | RF-01, RF-02, RF-05 | done |
| T-02 | Cache por (pergunta, estratégia, modelo) | T-01 | RF-04 | done |
| T-03 | `search` usa query expandida só no canal semântico | T-01 | RF-03 | done |
| T-04 | Flags `--expand` em `bench`, `search` e `qa` | T-03 | RF-06, RF-07 | done |
| T-05 | Medição contra a baseline 0,440 / 0,246 nas duas estratégias | T-01..T-04 | — | done |

## Ordem

T-01 → T-02 → T-03 → T-04 → T-05

## Definição de pronto (por task)

Teste RED nascido antes da implementação, falhando por `AssertionError`; GREEN com a suíte inteira verde; `ruff check kb tests` limpo.

T-05 é o gate: sem ganho, a hipótese da 017 cai e o resultado é registrado como negativo — não se ajusta prompt até o número subir.
