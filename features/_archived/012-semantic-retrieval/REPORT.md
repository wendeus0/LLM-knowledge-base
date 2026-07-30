# REPORT — 012-semantic-retrieval

**Data:** 2026-07-15
**Status:** `DONE_WITH_CONCERNS` — mergeado em `main` (f694190, 2026-07-30); concerns abaixo
**Ciclo:** SPEC → RED (16 testes) → GREEN → REFACTOR → VALIDATE → dogfood no vault real

## O que mudou

- **`kb/embeddings.py` (novo):** `embed_texts` via endpoint OpenAI-compat do Ollama (env `KB_EMBED_MODEL`/`KB_EMBED_BASE_URL`, defaults Nomic local); `build_index` incremental por hash sha256 (novo/alterado re-embeda; removido sai; inalterado reusa), com prefixos de task do Nomic (`search_document:`/`search_query:`), truncamento contado e escrita atômica em `kb_state/embeddings.json`; `load_index` valida modelo (divergência → None → fallback); `index_status` (cobertura, stale, notas de ausência/corrupção/divergência); `semantic_ranking` por cosseno (falha de embed na query degrada para `[]`).
- **`kb/search.py`:** canal semântico como 4º ranking na fusão RRF quando há índice válido; sem índice, comportamento lexical intacto. `find_relevant` (usado pelo `qa`) herda o canal automaticamente.
- **`kb/cli.py`:** sub-app `kb index build [--force]` e `kb index status`.

## Validação

- 16 testes novos (7 unit + 9 integration), nascidos RED; embedder fake como única fronteira mockada; cosseno verificado com vetores trabalhados à mão.
- Suíte completa: **440 passed**, cobertura **92%**, ruff limpo.
- **Dogfood no vault real:** 2.059 artigos indexados em ~56s (dim 768, 388 truncados). Query de controle "como evitar que uma falha em um componente derrube o sistema inteiro": híbrido → falhas-em-cascata, modos-de-falha, deixe-falhar, circuit-breaker; lexical puro → 1 acerto + glossário de DDD irrelevante. Fecha o P2 "Embeddings + RAG híbrido" do PENDING_LOG (2026-04-03).

## Riscos / dívida (concerns)

- **388/2059 artigos truncados** a 8k chars no embedding — chunking por seção é o próximo candidato de qualidade (fora de escopo declarado na SPEC; medir miss rate antes).
- `~/vault/wiki/summaries/` duplica artigos da raiz — o índice embeda os dois e resultados podem vir em dobro (ex.: `circuit-breaker.md` 2x no top-5). Decidir se `summaries/` entra no índice ou vira infra (`_summaries`).
- Índice não se atualiza automaticamente após `compile`/`heal` — rodar `kb index build` manual ou acoplar a um job (`jobs cron`) em iteração futura.
- Embed da query adiciona ~1 chamada Ollama por busca; com Ollama fora, busca degrada silenciosamente para lexical (por design).

## Próximos passos

1. Commit das features 011+012 quando solicitado.
2. Decidir tratamento de `summaries/` no índice.
3. Roadmap (DOMAIN 011): módulos paper/artigo (consomem este retrieval) → API + app visual.
