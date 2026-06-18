# Handoff — opencode go: kimi-k2.7-code + topic routing

Data: 2026-06-18

## Escopo
`kb/client.py`, `kb/compile.py`

## Resumo
- **client.py**: `OPENCODE_GO_ALLOWED_MODELS` atualizado para o conjunto real exposto pelo provider opencode go (`/v1/models`), habilitando `kimi-k2.7-code` (+ kimi-k2.6, minimax-m3/m2.7/m2.5, glm-5.1, deepseek-v4-pro/flash, qwen3.x, mimo*, hy3-preview). O set anterior (`{kimi-k2.5, minimax-2.7, glm-5}`) estava desatualizado e rejeitava modelos válidos do provider.
- **compile.py**: novo `_topic_from_source()` — o tópico passa a ser inferido da pasta de origem `raw/<topic>/...`, sobrepondo o palpite do LLM, e reescreve a linha `topic:` do frontmatter compilado. Corrige roteamento inconsistente (artigos com source em `raw/harness/` caíam em `wiki/ai` ou `general`).

## Validação
- `validate_provider_model_compatibility(..., 'kimi-k2.7-code')` aceita sem erro.
- Compile do tópico `harness` roteou 14 chunks corretamente para `wiki/harness/` (vault `~/work/llm-wiki`).

## Next steps
- Testes para `_topic_from_source` (`raw/books/` → general; `raw/harness/` → harness).
- Avaliar sincronizar o allowlist com `/models` dinamicamente (hoje hardcoded).
