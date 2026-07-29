# REPORT — 013-context-budget

**Data:** 2026-07-15
**Status:** `DONE` (código local; commit pendente)
**Ciclo:** plano aprovado (`~/.claude/plans/vamos-tentar-ajustar-primeiro-cheeky-fern.md`) → SPEC → RED (12 testes) → GREEN → suíte → verificação E2E

## O que mudou

- **`kb/config.py`:** tabela `RETRIEVAL_PROFILES` (fast/deep/paper/article) + `get_retrieval_profile` (erro claro p/ perfil desconhecido; `KB_QA_DOC_CHARS` sobrepõe doc_chars de qualquer perfil) + `qa_doc_chars()`.
- **`kb/router.py`:** `cap_text` (corte em fronteira de parágrafo + marcador `[... truncado]`; corte duro se parágrafo único excede); cap aplicado a seeds, extras de traversal e rota raw; `build_context` parametrizado por `doc_chars`/`traversal_budget` (inclusive no fallback).
- **`kb/qa.py` + `kb/cmds/qa/run.py` + `kb/cli.py`:** perfil fluindo fim-a-fim; `kb qa` default = `fast` (top_k 3, cap 4k, traversal budget 1.5k); flags `--deep` (top_k 5, cap 8k) e `--top-k N` (min=1).
- **`.env` local** (gitignored): `KB_DATA_DIR=~/vault` — elimina o footgun de rodar `kb` contra o repo.
- **`start-bonsai-server.sh`:** `--ubatch-size 1024` (experimento medido: 32.7 → 42.1 tok/s pp, +29%; 2048 piora para 28.1 por pressão de memória).

## Validação

- 12 testes novos (8 unit + 4 integration), nascidos RED; cap com exemplos trabalhados à mão; perfis e overrides testados; suíte completa **452 passed**, cobertura 93%, ruff limpo. 8 testes antigos atualizados para o novo contrato de kwargs (mudança intencional da SPEC).
- **E2E (3 perguntas de referência, perfil fast):**

| Pergunta | Antes | Depois | Prompt |
|---|---|---|---|
| Bounded context vs subdomínio | ~5min | **2m11s** | 10.465 → 2.795 tokens |
| Cardinalidade em observabilidade | ~5min | **1m42s** | 8.672 → 1.917 tokens |
| Bulkhead | — | **1m13s** | 1.953 tokens |

Qualidade preservada: todas as respostas corretas e citando os artigos-fonte (`[[mapas-de-contexto]]`, `[[armazenamento-eficiente...]]`, `[[padrao-bulkheads]]`).

## Riscos / dívida

- Perfis `paper`/`article` existem e são testados, mas só ganham consumidores reais nos módulos de autoria (features futuras).
- Cap de 4k corta a cauda de 40% dos artigos — se o bench (014) mostrar perda de fidelidade em perguntas profundas, `--deep` é a válvula; chunking é a solução estrutural.
- pp em produção ficou ~28-32 tok/s (vs 42 isolado) — sistema carregado; nada a agir.

## Próximos passos (plano aprovado)

1. Feature 014 — `kb bench` + golden set (gate da decisão Bonsai 8B).
2. Chunking + re-rank + sumários-como-sinal (SPEC própria).
3. Investigação tensor API → PR ao fork (time-box 1 sessão de diagnóstico).
4. Commits 011–013 quando o dono pedir.
