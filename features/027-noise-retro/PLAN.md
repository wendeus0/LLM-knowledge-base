# PLAN — 027-noise-retro

**Branch:** `feat/027-noise-retro`
**Data:** 2026-08-05
**Spec:** `features/027-noise-retro/SPEC.md` · **Domain:** `features/027-noise-retro/DOMAIN.md`

## Contexto técnico

| Campo | Valor |
|---|---|
| Alvo | `kb/noise.py`, `kb/cli.py` (sub-app noise), testes |
| Estado atual | `scan_corpus(raw_dir, wiki_dir)` varre só `raw_dir/books/*/metadata.json` (`kb/noise.py:136`) e devolve `list[Path]`; `archive_candidates` achata hierarquia e não versiona; o commit do apply stage-a só destinos (`kb/cli.py:1154`) |
| Reuso | `move_to_archive(candidates: list[dict], archive_dir, *, dry_run)` (`kb/archive.py:133`) já preserva hierarquia (dest vem do caller) e faz backup versionado; `_summary_path` (`kb/compile.py:344`) dá o espelho do summary; `update_index` (`kb/compile.py:587`); `refresh_embeddings_index` (`kb/embeddings.py:164`) |
| Estratégia de testes | test-red com fixtures de vault temporário; 1 condição binária de risco (output estrutural estável — o candidato estruturado vira contrato do relatório HITL) |

## Desenho

1. **`NoiseCandidate`** (dataclass congelada — contrato do relatório HITL e do apply): `path: Path`, `kind: "chapter"|"article"`, `category: str`, `book: str | None` (todos os livros possíveis, separados por ` | ` em colisão de basename), `chapter_title: str | None`, `summary: Path | None`. `scan_corpus` devolve `list[NoiseCandidate]`.
2. **Multi-root**: raízes = `[raw_dir / "books"]` + diretórios de 2º nível de `data_dir/library` que contêm `metadata.json` — implementado como glob `library/*/*/metadata.json` a partir de `DATA_DIR`, mantendo `_chapter_path_inside_book` (contenção) por raiz. Assinatura vira `scan_corpus(raw_dir, wiki_dir, library_dir=None, taxonomy=None)` com default `DATA_DIR/library` resolvido no CLI (função pura recebe paths — testável).
3. **Casamento**: passada B inalterada na lógica (source-basename ∈ ruidosos, título como fallback), mas registra de qual livro/capítulo veio o match para preencher o candidato.
4. **Apply**: monta `[{source: artigo, dest: ARCHIVE_DIR/rel}]` (+ summary quando existir) e delega a `move_to_archive`; commit recebe origens **e** destinos; ao final `update_index(no_commit=...)` + `refresh_embeddings_index()`. Capítulo-fonte nunca entra na lista de move.
5. **Relatório**: o CLI de `scan` imprime tabela book-qualified (base do relatório HITL do A3); sem formato novo de arquivo — o lote A3 salva a saída como markdown no vault.

## Condições binárias de risco (gate test-design)

| Condição | Presente? |
|---|---|
| Output estrutural estável | **sim** — o candidato estruturado é o contrato do relatório HITL e do apply |
| Demais (HTTP, DB real, UI, contrato entre serviços, E2E browser) | não |

→ `test-design` com `test-red` como camada base; foco em snapshot do formato de saída + propriedades do move.

## Riscos

- Mudar o retorno de `scan_corpus` quebra os 4 testes de contenção que fixam a estrutura antiga — reescritos junto (previsto na SPEC).
- `move_to_archive` valida contenção do dest sob `archive_dir` — manter os destinos calculados via `relative_to(WIKI_DIR)`.
- Refresh de embeddings depende do servidor `:1234`; no apply, falha de refresh degrada com aviso, não aborta o move (mesma política do compile).
