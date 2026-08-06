# PLAN — 029-chapters-regroup

**Branch:** `feat/029-chapters-regroup`
**Data:** 2026-08-06
**Spec:** `features/029-chapters-regroup/SPEC.md` · **Domain:** `features/027-noise-retro/DOMAIN.md`

## Contexto técnico

| Campo | Valor |
|---|---|
| Alvo | `kb/fsutil.py` (helper), `kb/lint.py:33,53`, `kb/heal.py:85-104`, `kb/archive.py:44-45,72`, `kb/compile.py:592-593`, `kb/stats.py:4-8`, novo `kb/regroup.py`, `kb/cli.py` |
| Reuso | `graph._e_artigo` (semântica de referência), `archive.move_to_archive`, `state.mark_archived`/`update_article_path`/`load_manifest`, `compile.update_index`, `refresh_embeddings_index`, maquinaria de lote HITL das 027/028 |
| Estratégia de testes | test-design: I/O em store real (move em massa + manifest) e output estrutural (plano de move é contrato do gate humano) |

## Desenho

1. **C1 — `kb/fsutil.iter_articles(wiki_dir)`**: generator com a semântica de `graph._e_artigo` (`_`/`.` em qualquer componente, symlink fora). Adotado em: `lint.find_ambiguous_wikilinks` e `lint_wiki`; `heal._sample_paths`; `archive.find_orphans`/`find_by_age`; `compile.update_index`; `stats`. `graph._e_artigo` passa a delegar ao helper (uma semântica, um lugar).
2. **C2 — heal sem unlink**: `_remove_stub` usa `move_to_archive` (dest `ARCHIVE_DIR/<rel>`), remove o `_backup` caseiro para stubs (o backup versionado do archive cobre) e chama `mark_archived`. `.heal_backup` legado permanece intocado.
3. **C3 — `kb/regroup.py`**: `plan_regroup(wiki_dir, manifest)` → grupos `{book: [(artigo, destino)]}` + `unresolved: [artigo]`; destinos `wiki/_chapters/<book-slug>/<nome>` e summary espelho em `wiki/_summaries/_chapters/<book-slug>/`. `apply_book(book)` move via `move_to_archive`-like (mesma contenção, mas destino é `_chapters/` — usar move com `atomic`/`shutil.move` + backup versionado próprio), `update_article_path`, `update_index`, refresh. Book-slug: slugify do nome do livro (nomes vindos de metadata têm " -- Anna's Archive" etc. — sanitizar).
4. **C4 — ops**: preflight + tag `pre-regroup-<data>` → `regroup scan` → relatório por livro (contagem, exemplos, unresolved) → aprovação explícita → apply livro a livro (commit por livro) → `kb index build` + smoke + tela.

## Riscos

- `update_index`/embeddings ficam consistentes porque C1 os ensina a ignorar `_chapters/` ANTES de qualquer move (ordem C1 → C3 é hard gate).
- Slug de livro com nomes sujos de metadata → sanitização com teste.
- 126 `unresolved` permanecem na wiki — visíveis no relatório, decisão humana posterior.
- Bench/golden perdem objeto após o move — aceito (ADR), registrado.
