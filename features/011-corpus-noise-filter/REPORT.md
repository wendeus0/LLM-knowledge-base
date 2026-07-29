# REPORT — 011-corpus-noise-filter

**Data:** 2026-07-15
**Status:** `DONE` (código local; commit pendente de solicitação do dono)
**Ciclo:** grilling (DOMAIN) → SPEC → RED (17 testes) → GREEN → REFACTOR → VALIDATE

## O que mudou

- **`kb/noise.py` (novo):** taxonomia default PT/EN de capítulos-ruído (agradecimentos, dedicatória, prefácio, elogios, encerramento = epílogo/posfácio — Conclusão fica, colofão, sobre o autor, copyright, índice) com override por vault (`kb.toml`, seção `[noise].extra`); `classify_chapter` (match por título inteiro ou prefixo com fronteira — falso-amigo no meio do título não corta); `split_noise`; `scan_corpus` (raw/books/*/metadata.json + artigos wiki via frontmatter `source`); `archive_candidates` (move, nunca deleta; conflito sufixa).
- **`kb/book_import_core.py`:** capítulos ganham `title_source` (heading/toc/fallback); `convert_book(keep_noise=False)` filtra ruído por default; `metadata.json` ganha `keep_noise`, `excluded_chapters` (título+categoria), `ambiguous_chapters` e `noise_classification_skipped` (livro sem títulos utilizáveis → nada excluído + warning).
- **`kb/cli.py`:** `import-book --keep-noise`; relatório pós-import (`excluído (ruído): ...`, `mantido (não classificado): ...`, aviso de classificação impossível); sub-app `kb noise scan` (dry-run) e `kb noise apply [--commit]`.

## Validação

- 17 testes novos (7 unit + 10 integration), todos nascidos RED com `AssertionError` pelo motivo certo.
- Suíte completa: **422 passed**, cobertura **92%** (gate 85%), `ruff` limpo.
- Regressão detectada e corrigida durante o ciclo: relatório pós-import tolera `metadata.json` ausente/ilegível (mocks de testes antigos).

## Riscos / dívida

- **Breaking default**: `import-book` agora exclui ruído por padrão; mitigado por `--keep-noise` e por arquivar (nunca deletar) no retroativo.
- `scan_corpus` casa artigo wiki por **nome** do arquivo de capítulo (`source:` do frontmatter), não por caminho — colisão teórica entre livros com capítulo-ruído homônimo (ambos seriam ruído; impacto baixo).
- Classificação assistida por LLM local para títulos criativos: deferida até medir o miss rate da heurística no vault real (registrado na SPEC, Notas).

## Próximos passos

1. **Manual (dono):** `kb noise scan` no vault real e revisar a lista antes do primeiro `apply` (passo Manual da SPEC).
2. Commit da feature quando solicitado.
3. Feature 012 — retrieval semântico com embeddings Nomic (Fase 2 do ADR-0013), próxima fatia do roadmap (`DOMAIN.md`).
