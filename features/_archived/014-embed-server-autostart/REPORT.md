# REPORT — 014-embed-server-autostart

**Data:** 2026-07-28
**Status:** `DONE` (código local; commit pendente de push)
**Ciclo:** SPEC → PLAN/TASKS → RED (22 testes) → GREEN → suíte → validação manual no servidor real

## O que mudou

- **`kb/embed_server.py` (novo):** `probe()` consulta `/v1/models` e devolve `ServerState(reachable, models, error, endpoint)`; `model_available()` como predicado puro; `autostart()` executa comando externo e faz poll até o endpoint responder, com teto; `ensure_server()` orquestra probe → autostart opcional → probe, com **uma única tentativa**. Duas fronteiras de efeito isoladas (`_http_get_json`, `_run_command`), ambas monkeypatcháveis — nenhum teste toca rede ou processo.
- **`kb/cli.py`:** `kb index status` ganha bloco de servidor — endpoint, alcançabilidade e disponibilidade do modelo configurado, distinguindo "inacessível" de "modelo ausente" (com a lista dos disponíveis).
- **`kb/search.py`:** degradação para lexical deixa de ser silenciosa — aviso em `stderr`, uma vez por execução, nomeando a causa (índice ausente vs. servidor sem resposta) e a ação corretiva. `stdout` permanece parseável.
- **`kb/embeddings.py`:** mensagem de erro do `build_index` passa a nomear o endpoint configurado e o comando real de start; removidas as três menções a Ollama (módulo docstring, docstring de `embed_texts`, mensagem de erro) — o runtime é LM Studio desde a implementação da 012, e o artefato descrevia outro sistema.

**Fora do escopo declarado da SPEC, corrigido no mesmo ciclo** (débito visível, `repo_mode: solo`):

- **`kb/search.py:_iter_docs`** excluía apenas `_index.md`, então a busca lexical indexava `_summaries/` (1.022 arquivos) e `_sources/` (712). Agora aplica a mesma convenção `_*` do índice semântico — uma única definição de corpus para os dois canais. Encontrado durante a validação manual: `kb search "resiliencia de sistemas"` devolvia `_summaries/fundamentos-de-sistemas-de-dados.md` no topo.

## Validação

- 22 testes novos (15 unit em `test_embed_server.py`, 4 integration em `test_index_server_cli.py`, 3 unit em `test_search_degradation.py`), todos nascidos RED por `AssertionError` — o stub inicial de `embed_server` existiu só para tirar o `ImportError` do caminho.
- Suíte completa: **477 passed**, cobertura **93%**, ruff limpo.
- **Validação manual no servidor real (LM Studio, `nomic-embed-text-v2-moe`):**

| Cenário | Resultado |
|---|---|
| Servidor no ar | `servidor: ok em http://localhost:1234/v1 — modelo disponível` |
| Servidor parado, `index status` | `inacessível ... (Connection refused)` + instrução de start |
| Servidor parado, `search` | aviso em stderr; resultado lexical entregue normalmente |
| Servidor parado, `KB_EMBED_AUTOSTART=1` | **servidor subiu sozinho e reportou ok, em 0,9s** |

## Riscos / dívida

- O aviso de degradação usa flag de módulo (`_semantic_warned`) para garantir "uma vez por execução". Funciona por processo; um daemon de vida longa avisaria só na primeira vez. Aceitável para CLI.
- `autostart` só sobe o servidor — não derruba nem reinicia. Ciclo de vida completo ficou fora de escopo.
- O poll do autostart usa intervalo fixo de 0,5s até o teto; sem backoff. Suficiente para start local (medido em ~0,9s no total).
- A correção de `_iter_docs` muda o conjunto de resultados da busca lexical no vault real: 1.734 arquivos de infra saíram do corpus. É a intenção, mas é mudança de comportamento observável sem SPEC própria.

## Próximos passos

1. Feature 015 — cobertura real do `index status` e invalidação automática do índice após `compile`/`heal` (concern herdado do REPORT de 012).
2. Feature 016 — `kb bench` + golden set: sem ele, comparar `v1.5` × `v2-moe` ou avaliar chunking é opinião.
3. Feature 017 — chunking por seção (388 dos 2.059 artigos foram truncados a 8k no índice original).
