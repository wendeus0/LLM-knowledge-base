---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-04-06

**O que foi feito:**
- revisão da violation P2 do PR#15 (`feat/rich-book-import-metadata`)
- fix aplicado em `kb/book_import_core.py:173`: `_resolve_href` agora recebe `unquote(src)` para alinhar paths resolvidos com keys do `image_map` (built from decoded manifest hrefs)
- PR#15 description atualizada via `gh pr edit 15`
- sprint-close executado: logs, memória e handoff atualizados

**O que falta:**
- merge PR#14 (`feat/wikilink-traversal`) e PR#15 (`feat/rich-book-import-metadata`)
- smoke test real com OpenCode Go
- política operacional de sensibilidade
- instalar Shell Commands plugin manualmente no Obsidian

**Próximo passo recomendado:**
1. Verificar aprovações e mergear PR#14 e PR#15
2. `git checkout main && git pull` para atualizar local
3. Rodar smoke test: `pip install -e .[llm]` → `kb import-book <arquivo.epub> --compile` → `kb qa "pergunta"` → `kb heal --n 3` → `kb lint`

**Prompt de retomada:**
> Retome o projeto `kb` em 2026-04-06. Sprint entregou: outputs store (PR#12), URL ingest (PR#13), wikilink traversal (PR#14 — aguardando merge), rich book metadata (PR#15 — aguardando merge, fix de URL-encoding aplicado). Próxima ação: mergear PRs abertos e rodar smoke test real com OpenCode Go.

---

## Sessão — 2026-04-04

**O que foi feito:**
- triage completo do estado do projeto (session-open + technical-triage)
- criado `wiki/.obsidian/` com configuração completa do vault Obsidian + Shell Commands plugin pré-configurado (hotkeys Ctrl+Shift+C/Q/H/L/S)
- `PENDING_LOG.md`: Obsidian integration marcada como concluída
- sprint-close executado

**Prompt de retomada:**
> Retome do sprint fechado em 2026-04-04 no projeto `kb`. Prioridade: resolver trabalho não commitado em `feat/readme-arch-docs` (já mergeado). Criar branch correto, passar pelo workflow e validar o fluxo real com OpenCode Go.

---

## Sprint close — 2026-04-03

**O que foi feito neste ciclo:**
- fundação inspirada em Pal: routing por fonte, stores, manifesto, summaries, jobs, guardrails, flags `--allow-sensitive`/`--no-commit`
- ADRs `0006` e `0007` criados
- baseline validada com **85 testes passando**

**Prompt de retomada:**
> Retome o projeto `kb` após o sprint de fundação inspirada em Pal. Primeiro revise/feche o fluxo git da branch atual; depois rode o smoke test real com OpenCode Go.
