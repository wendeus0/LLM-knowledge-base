# TASKS — Archive: mover artigos stale/órfãos para archive/

**Spec:** features/006-kb-archive/SPEC.md
**Plan:** features/006-kb-archive/PLAN.md
**MVP:** tasks [P1] completas

## Fase 1 — Setup

- [T-001] [P1] Adicionar `ARCHIVE_DIR` em `kb/config.py` e garantir criação no startup

## Fase 2 — Foundational (P1)

- [T-002] [P1] Criar `kb/archive.py` com função `collect_candidates(wiki_dir, stale=False, older_than=None) -> list[dict]`
- [T-003] [P1] [P] Implementar `find_orphans(wiki_dir) -> list[Path]` via regex de wikilinks
- [T-004] [P1] [P] Implementar `find_by_age(wiki_dir, days) -> list[Path]` via `st_mtime`
- [T-005] [P2] [P] Implementar `find_stale(wiki_dir, stale_threshold_days) -> list[Path]` (proxy de stale_pct)
- [T-006] [P1] Implementar `move_to_archive(candidates, archive_dir, dry_run=False) -> list[dict]` com `shutil.move`
- [T-007] [P1] Implementar `render_preview_table(candidates, console)` usando rich Table

## Fase 3 — User stories (P1→P2→P3)

- [T-008] [P1] Adicionar comando `kb archive` em `kb/cli.py` com flags `--stale`, `--older-than`, `--dry-run`
- [T-009] [P1] Wire `archive` command para chamar `collect_candidates` + `move_to_archive` + preview
- [T-010] [P2] Suportar overwrite silencioso quando destino já existe em `archive/`
- [T-011] [P1] Tratar wiki inexistente/vazia com erro amigável e exit 1
- [T-012] [P1] Validar `--older-than N` com N > 0
- [T-013] [P2] Tratar falhas de permissão no move: logar e continuar

## Fase 4 — Polish

- [T-014] [P1] Escrever `tests/unit/test_archive.py` cobrindo orphans, age, dry-run, estrutura preservada
- [T-015] [P1] Escrever `tests/integration/test_archive_cli.py` cobrindo chamada Typer e tabela de preview
- [T-016] [P1] Rodar `pytest` e `ruff check kb`; garantir verde

---

## Matriz de dependências

| Task  | Depende de                 | Pode ser paralela com      |
| ----- | -------------------------- | -------------------------- |
| T-001 | —                          | T-002, T-003, T-004, T-005 |
| T-002 | T-001                      | T-003, T-004, T-005        |
| T-003 | T-002                      | T-004, T-005               |
| T-004 | T-002                      | T-003, T-005               |
| T-005 | T-002                      | T-003, T-004               |
| T-006 | T-002, T-003, T-004, T-005 | T-007                      |
| T-007 | T-002                      | T-006                      |
| T-008 | T-006, T-007               | —                          |
| T-009 | T-008                      | —                          |
| T-010 | T-006                      | T-009                      |
| T-011 | T-008                      | T-010                      |
| T-012 | T-008                      | T-010, T-011               |
| T-013 | T-006                      | T-009, T-010, T-011, T-012 |
| T-014 | T-006, T-007               | T-008, T-009               |
| T-015 | T-009                      | T-014                      |
| T-016 | T-014, T-015               | —                          |
