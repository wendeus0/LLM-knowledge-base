# TASKS — 016-bench-golden-set

| ID | Task | Depende de | RF | Estado |
|---|---|---|---|---|
| T-01 | `evaluate_case()` e `aggregate()` — recall@k, MRR, caso inválido | — | RF-01, RF-05, RF-07 | done |
| T-02 | `load_golden()` — leitura, validação, ausência e JSON inválido | — | RF-02, RF-06 | done |
| T-03 | `seed_golden()` — casos título→artigo a partir do corpus | T-02 | RF-04 | done |
| T-04 | `run_bench()` — orquestra golden → search → métricas, por modo | T-01..T-03 | RF-01, RF-03 | done |
| T-05 | Comando `kb bench` com flags e saída `--json` | T-04 | RF-03, RF-05, RF-08 | done |

## Ordem

(T-01 ‖ T-02) → T-03 → T-04 → T-05

## Definição de pronto (por task)

Teste RED nascido antes da implementação, falhando por `AssertionError`; GREEN com a suíte inteira verde; `ruff check kb tests` limpo.
