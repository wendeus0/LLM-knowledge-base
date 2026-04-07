---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-04-07 (Sprint close)

**O que foi feito:**
- Smoke test completo com OpenCode Go real: `search`, `lint`, `qa`, `heal`, `import-book --compile` OK
- EPUB "Building Applications with AI Agents" importado → 12 artigos em `wiki/ai/`
- `docs/SENSITIVE_CONTENT_POLICY.md` criado — critérios para `--allow-sensitive` e `--no-commit`
- pytest-cov instalado; 80% cobertura baseline; HTML em `htmlcov/`
- ADR-0001 atualizado — A3 (extração de pacote) rejeitada formalmente
- Root cause de code fence wrapping identificado e corrigido:
  - SYSTEM prompt em `compile.py` atualizado com instrução "SEM code fences"
  - `_strip_outer_fence()` adicionado como defesa defensiva em `compile_file()`
  - 25 artigos em `wiki/ai/` e `wiki/summaries/ai/` corrigidos manualmente
- PR#19 aberto (branch `feat/wikilink-traversal`) com todas as entregas do sprint

**O que falta:**
- Merge PR#19 (feat/wikilink-traversal → main)
- Corrigir 8 testes falhando em `test_web_ingest.py` (mock setup pré-existente)
- Instalar Shell Commands plugin no Obsidian (passo manual do usuário)
- Refinar guardrail para falso positivo de nomes de variável em código técnico

**Métricas do sprint:**
- Testes: 113 passando, 8 falhando (pré-existentes, test_web_ingest.py)
- Cobertura: 80% total
- Wiki: 14 artigos em wiki/ai/, 11 summaries
- ADRs: 0001–0009

**Prompt de retomada:**
> Retome o projeto `kb` após o sprint de 2026-04-07. As entregas deste sprint: smoke test real OK, EPUB importado (12 artigos wiki/ai/), política de sensibilidade criada, pytest-cov 80%, fix de code fence em compile.py, PR#19 aberto. Próximas ações: (1) mergear PR#19; (2) corrigir 8 testes falhando em test_web_ingest.py (mock AttributeError); (3) instalar Shell Commands no Obsidian (passo manual).

---

## Sessão — 2026-04-06

**O que foi feito:**
- revisão da violation P2 do PR#15 (`feat/rich-book-import-metadata`)
- fix aplicado em `kb/book_import_core.py:173`: `_resolve_href` agora recebe `unquote(src)` para alinhar paths resolvidos com keys do `image_map` (built from decoded manifest hrefs)
- PR#15 description atualizada via `gh pr edit 15`
- sprint-close executado: logs, memória e handoff atualizados

---

## Sprint close — 2026-04-03

**O que foi feito neste ciclo:**
- fundação inspirada em Pal: routing por fonte, stores, manifesto, summaries, jobs, guardrails, flags `--allow-sensitive`/`--no-commit`
- ADRs `0006` e `0007` criados
- baseline validada com **85 testes passando**
