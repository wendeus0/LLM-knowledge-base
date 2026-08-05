# REPORT — 027-noise-retro

**Estado:** `DONE`
**Branch:** `feat/027-noise-retro`

## Contexto

Primeira das três features do esforço de higiene do corpus (etapas 1–3 do ADR-0018, plano aprovado em 2026-08-05). `kb noise scan` devolvia 0 candidatos no vault real: varria `raw/books/`, e os 34 livros extraídos vivem em `library/`. O `apply` tinha três defeitos latentes: achatava a hierarquia no `archive/`, não versionava colisão e o commit registrava só o destino, deixando a deleção fora.

## Mudanças

- `kb/noise.py`: `scan_corpus` multi-root (`raw/books/*` + `library/*` e `library/*/*`), devolvendo `NoiseCandidate` estruturado (path, kind, categoria, livro(s), título do capítulo, summary espelho). Capítulo-fonte de `library/` qualifica o artigo mas **nunca** é candidato a move. Colisão de basename entre livros lista todos os livros possíveis em vez de atribuir o primeiro — sem manifest, atribuir um só seria chute apresentado como fato. `archive_candidates` (achatava, não versionava) foi removida.
- `kb/cli.py`: `noise scan` imprime categoria + arquivo + proveniência; `noise apply` delega a `archive.move_to_archive` (hierarquia + backup versionado), move o summary junto, commita **origem e destino**, regenera `_index.md` e atualiza embeddings de forma incremental.

## Validação

**979 passed** (16 testes novos/reescritos de noise), ruff limpo, appeasement exit 0, cobertura 93%.

**Lote real (T-003, HITL):** preflight (tree limpa, tag `pre-noise-retro-2026-08-05`, cron sem kb) → relatório de 40 candidatos book-qualified → aprovação do dono ("aplicar os 40") → apply --commit. Resultado no vault: **79 arquivos movidos** (40 artigos + 39 summaries), commit `bc5d5c9`, `_index.md` −40 entradas, índice de embeddings descartou 40 vetores sem re-embedar, wiki de 1.042 → **1.002 artigos vivos**. Tela conferida: home com 12 recentes, zero paratexto.

Achado do lote que virou melhoria antes do apply: a primeira versão do scan atribuía o livro errado em colisão de basename (ex.: artigo do *Working Effectively* rotulado como *Observability Engineering*). Corrigido com teste antes do lote — o relatório HITL mostrava proveniência falsa.

## Riscos e dívida

| Item | Estado |
|---|---|
| 8 dos 40 arquivados têm cara de resumo-de-livro (nasceram de capítulo de índice/capa) | Decisão explícita do dono; o conteúdo volta melhor via artigo de tema no reagrupamento. Reversível por git (`pre-noise-retro-2026-08-05`) |
| Falso positivo residual por título ("Index" como capítulo real) | Absorvido pelo gate humano; nenhum caso no lote real |
| Reconciliação completa das políticas de remoção (V7) | Feature 029 (C2) |
| Manifest não sabe dos 40 arquivados | Sem entrada prévia — nada ficou dangling. A manutenção de manifest em archive nasce na 028 (B4) |

## Próximos passos

Feature 028 (`provenance-dedup-topics`): manifest schema v2 + backfill (B1/B2), lote de proveniência (B3), dedup de ingestão (B4/B5), topics (B6–B8). C1 da 029 (helper `_*`) pode começar em paralelo.
