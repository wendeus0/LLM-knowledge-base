# PLAN — 014-embed-server-autostart

## Arquitetura

Um módulo novo, `kb/embed_server.py`, com três responsabilidades puras e uma fronteira de efeito:

| Função | Responsabilidade | Fronteira |
|---|---|---|
| `probe(base_url, timeout)` | Consulta `/v1/models`; devolve `ServerState(reachable, models, error)` | rede — monkeypatchável |
| `model_available(state, model)` | Predicado puro sobre a lista devolvida | pura |
| `autostart(cmd, timeout)` | Executa o comando e aguarda o endpoint responder | processo — monkeypatchável |
| `ensure_server(...)` | Orquestra probe → (autostart se habilitado) → probe; uma tentativa | compõe as acima |

`kb/embeddings.py` passa a consumir `ensure_server` em dois pontos: `build_index` (falha alto com mensagem correta) e o caminho de consulta (degrada com aviso).

**Por que módulo separado:** `embeddings.py` hoje mistura índice, cosseno e fronteira de rede. Estado de servidor é outra preocupação, tem outra fronteira (processo) e precisa ser testável sem tocar em índice.

## Decisões

1. **Autostart é opt-in** (`KB_EMBED_AUTOSTART`, default off). O caminho padrão nunca inicia processo — subir GUI sem pedido é surpresa, e a ausência do canal semântico já será visível pelo aviso.
2. **Uma tentativa por execução.** Retry de start é caro e mascara problema de configuração.
3. **Aviso em stderr, uma vez por execução.** stdout continua parseável; repetir por query polui.
4. **O probe não é cacheado em disco.** É informação de momento; cachear cria estado stale que ninguém invalida.
5. **A mensagem de erro nomeia o endpoint configurado**, não um runtime hardcoded — foi exatamente o defeito que originou o RF-06.

## Condições binárias de risco

- Endpoint HTTP público: não
- I/O em DB real / migration: não
- UI com estado interativo: não
- Output estrutural estável: **sim** — `kb index status` ganha bloco novo e é lido por humano e por script
- Contrato HTTP entre serviços: não
- Fluxo E2E multi-página: não

Uma condição marcada → `test-design` orquestra `test-red` como camada base.

## Arquivos

| Arquivo | Mudança |
|---|---|
| `kb/embed_server.py` | novo — probe, autostart, ensure_server |
| `kb/embeddings.py` | consome `ensure_server`; corrige as três menções a Ollama (linhas 3, 28, 99) |
| `kb/cmds/index/run.py` ou `kb/cli.py` | bloco de servidor no `index status` |
| `tests/unit/test_embed_server.py` | novo |
| `tests/integration/test_index_server_cli.py` | novo |

## Riscos

- **Comando de autostart bloqueante:** `lms server start` retorna rápido, mas um runtime diferente pode não retornar. Mitigado por timeout próprio.
- **Falso negativo do probe:** servidor subindo lentamente é reportado como inacessível. Mitigado pelo poll até o teto no autostart.
- **Ruído do aviso:** se `kb qa` for chamado em loop por script, o aviso repete por processo. Aceito — é uma linha em stderr por execução.
