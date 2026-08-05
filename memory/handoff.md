# Handoff — PR #66 corrigido e Direção B implementada (fases 0–7 completas)

> Substitui o handoff de 2026-08-05 escrito no meio da Fase 2. Todas as 8 fases do plano aprovado foram executadas. **Nada commitado** — é tudo working tree.

## Onde está o plano

Os dois planos ficam fora do repositório, no diretório de planos do harness
(`~/.claude/plans/`): `olhe-o-id-do-distributed-bumblebee.md` (as 8 fases
originais) e `handoff-completo-salvo-em-enumerated-heron.md` (a retomada).

## Estado

- PR #66 `OPEN`, `headRefOid` = `af82323` = HEAD local. Nenhum push desde a pausa.
- Working tree: 44 arquivos alterados, 1025 inserções, 422 remoções, mais 6 arquivos novos (`kb/security.py`, `tests/unit/test_kb_security.py`, `tests/unit/test_study_db.py`, `tests/integration/conftest.py`, `study/templates/partials/review_body.html`, `study/static/vendor/`).
- Gate: `python -m pytest` → **963 passed**, cobertura 93% · `ruff check kb study tests` limpo.
- Fases 0–7: todas `completed`. O detalhamento por arquivo está em `features/026-plataforma-de-estudos/REPORT.md`, seção "Rodada de correção do PR #66 (2026-08-05)".

## Decisões desta rodada que valem lembrar

- **Dois tokens de acento.** `#b4551f` (a cor da imagem) é preenchimento; texto usa `--accent-ink` — `#a84d1c` no claro, `#f07a32` no escuro. O motivo é contraste WCAG AA: `#b4551f` como texto dá 4,02:1 sobre o bege e 3,63:1 sobre o escuro. Registrado em `docs/research/2026-08-01-kb-para-estudo/DESIGN.md`.
- **Guard de rating duplicado foi removido** de `study/web.py`: sobreviveu à mutação porque `study/review.py:14` já validava o intervalo.
- **`study.db` continua em `DATA_DIR`**, não em `kb_state/` — há teste explícito fixando isso (`test_study_annotations.py`). Entrou `/study.db*` no `.gitignore`.
- **`Form(...)` nativo não foi adotado**: exigiria `python-multipart` como dependência de runtime para ganho cosmético.
- Fase 4 (lote mecânico) foi delegada ao Codex via MCP com `model: gpt-5.6-luna` — `gpt-5.6-sol` e `gpt-5.2-codex` são recusados pelo conector com conta ChatGPT.

## Próximo passo

Commit + push + resposta aos bots do PR #66, via `git-flow-manager` — **só com pedido explícito do usuário**. Antes disso vale rodar `enforce-workflow` e `feature-scope-guard`.

Evidência visual da Direção B (não versionada): `.playwright-mcp/direcao-b-claro-final.png`, `direcao-b-escuro-topo.png`, `direcao-b-toast.png`.
