# TASKS — 014-embed-server-autostart

| ID | Task | Depende de | RF | Estado |
|---|---|---|---|---|
| T-01 | `probe()` — estado do servidor a partir de `/v1/models`, com timeout | — | RF-01 | done |
| T-02 | `model_available()` — predicado sobre a lista de modelos | T-01 | RF-02 | done |
| T-03 | `autostart()` — executa comando e aguarda endpoint, com teto | T-01 | RF-03, RF-07 | done |
| T-04 | `ensure_server()` — orquestra, respeitando o flag opt-in e a única tentativa | T-01..T-03 | RF-03, RF-04 | done |
| T-05 | `index status` exibe bloco de servidor (endpoint, alcançável, modelo) | T-01, T-02 | RF-01, RF-02 | done |
| T-06 | Aviso visível em stderr ao degradar, com causa e ação | T-04 | RF-05 | done |
| T-07 | `build_index` falha com runtime/endpoint/comando corretos; remover menções a Ollama | T-04 | RF-06 | done |

## Ordem

T-01 → T-02 → T-03 → T-04 → (T-05 ‖ T-06 ‖ T-07)

As três últimas são independentes entre si e podem ir em qualquer ordem depois de T-04.

## Definição de pronto (por task)

Teste RED nascido antes da implementação, falhando por `AssertionError`; GREEN com a suíte inteira verde; `ruff check kb tests` limpo.
