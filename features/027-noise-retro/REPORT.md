# REPORT — 027-noise-retro

**Estado:** `DONE`
**Branch:** `feat/027-noise-retro`

## Contexto

Primeira das três features do esforço de higiene do corpus (etapas 1–3 do ADR-0018, plano aprovado em 2026-08-05). `kb noise scan` devolvia 0 candidatos no vault real: varria `raw/books/`, e os 34 livros extraídos vivem em `library/`. O `apply` tinha três defeitos latentes: achatava a hierarquia no `archive/`, não versionava colisão e o commit registrava só o destino, deixando a deleção fora.

## Mudanças

- `kb/noise.py`: `scan_corpus` multi-root (`raw/books/*` + `library/*` e `library/*/*`), devolvendo `NoiseCandidate` estruturado (path, kind, categoria, livro(s), título do capítulo, summary espelho). Capítulo-fonte de `library/` qualifica o artigo mas **nunca** é candidato a move. Colisão de basename entre livros lista todos os livros possíveis em vez de atribuir o primeiro — sem manifest, atribuir um só seria chute apresentado como fato. `archive_candidates` (achatava, não versionava) foi removida.
- `kb/cli.py`: `noise scan` imprime categoria + arquivo + proveniência; `noise apply` delega a `archive.move_to_archive` (hierarquia + backup versionado), move o summary junto, commita **origem e destino**, regenera `_index.md` e atualiza embeddings de forma incremental.

## Validação

**985 passed** (22 testes novos/reescritos de noise), ruff limpo, appeasement exit 0, cobertura 93%.

**Lotes reais (T-003, HITL), dois com aprovação do dono:**

1. **Paratexto** — preflight (tree limpa, tag `pre-noise-retro-2026-08-05`, cron sem kb) → relatório de 40 candidatos book-qualified → aprovação → apply --commit. 79 arquivos movidos (40 artigos + 39 summaries), commit `bc5d5c9` no vault, wiki 1.042 → 1.002. Tela conferida: home sem paratexto.
2. **Sumários/TOC** — o review do PR #69 expôs que a taxonomia não cobria table-of-contents (o glossário do DOMAIN prometia); categoria `sumario` adicionada revelou +22 artigos-TOC → relatório delta → aprovação → apply --commit. 44 arquivos movidos, commit `734604e`, tag `pre-noise-sumarios-2026-08-05`, wiki em **980 artigos vivos**.

Dois achados viraram correção com teste antes de qualquer apply: (1) a primeira versão do scan atribuía o livro errado em colisão de basename — o relatório HITL mostrava proveniência falsa; (2) o review do PR #69 somou proveniência completa no merge raw×library, backup versionado dentro do commit, aviso de entrada de manifest e a categoria `sumario`.

## Riscos e dívida

| Item | Estado |
|---|---|
| 8 dos 40 arquivados têm cara de resumo-de-livro (nasceram de capítulo de índice/capa) | Decisão explícita do dono; o conteúdo volta melhor via artigo de tema no reagrupamento. Reversível por git (`pre-noise-retro-2026-08-05`) |
| Falso positivo residual por título ("Index" como capítulo real) | Absorvido pelo gate humano; nenhum caso no lote real |
| Reconciliação completa das políticas de remoção (V7) | Feature 029 (C2) |
| Manifest não sabe dos 40 arquivados | Sem entrada prévia — nada ficou dangling. A manutenção de manifest em archive nasce na 028 (B4) |

## Próximos passos

Feature 028 (`provenance-dedup-topics`): manifest schema v2 + backfill (B1/B2), lote de proveniência (B3), dedup de ingestão (B4/B5), topics (B6–B8). C1 da 029 (helper `_*`) pode começar em paralelo.
