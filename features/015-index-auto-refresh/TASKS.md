# TASKS — 015-index-auto-refresh

| ID | Task | Depende de | RF | Estado |
|---|---|---|---|---|
| T-01 | `refresh_embeddings_index()` — flag, env, probe, build, captura de exceção | — | RF-04, RF-05, RF-06 | done |
| T-02 | Chamada ao fim de `compile_many` + flag no CLI | T-01 | RF-01, RF-07 | done |
| T-03 | Chamada ao fim de `heal()` + flag no CLI | T-01 | RF-02, RF-07 | done |
| T-04 | Chamada no caminho `--to-wiki` de `qa` + flag no CLI | T-01 | RF-03 | done |

## Ordem

T-01 → (T-02 ‖ T-03 ‖ T-04)

## Definição de pronto (por task)

Teste RED nascido antes da implementação, falhando por `AssertionError`; GREEN com a suíte inteira verde; `ruff check kb tests` limpo.
