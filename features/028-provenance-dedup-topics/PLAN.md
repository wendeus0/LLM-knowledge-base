# PLAN — 028-provenance-dedup-topics

**Branch:** `feat/028-provenance-dedup-topics`
**Data:** 2026-08-05
**Spec:** `features/028-provenance-dedup-topics/SPEC.md` · **Domain:** `features/027-noise-retro/DOMAIN.md`

## Contexto técnico

| Campo | Valor |
|---|---|
| Alvo | `kb/state.py` (schema+manutenção), novo `kb/backfill.py`, novo `kb/dedup.py`, novo `kb/topics.py`, `kb/cli.py` (3 sub-apps), testes |
| Reuso | `scripts/measure_corpus_quality.py` (`source_candidates`, vetores normalizados do índice), `kb/embeddings.py` (`embed_texts` p/ capítulos ambíguos), `archive.move_to_archive`, padrão `heal._stamp_reviewed` p/ frontmatter, `kb/frontmatter.parse` |
| Estratégia de testes | test-design: 3 condições binárias de risco — output estrutural estável (manifest v2 é contrato), I/O em store real (manifest/frontmatter em lote), output não-determinístico (assign via LLM → casos com mock e restrição dura à taxonomia) |

## Desenho

1. **Schema v2 (`kb/state.py`)** — aditivo: `provenance`, `book`, `source` relativo a `DATA_DIR` (leitura tolera legado absoluto/relativo-a-RAW), `article` relativo a `WIKI_DIR` na escrita. Helpers novos: `mark_archived(article_path)` e `update_article_path(old, new)` — consumidos por `dedup apply` (e pela 029 no move). `find_compiled_entry` inalterado no contrato.
2. **Backfill (`kb/backfill.py`)** — pipeline puro: (a) indexar candidatos por basename em `library/**`, `wiki/_sources/**`, `raw/**`; (b) basename único → par; (c) múltiplos: conteúdo idêntico (hash normalizado) → par; senão cosseno artigo×capítulos candidatos (vetor do artigo vem do índice; capítulo embedado on-demand) com piso 0,75; (d) resto `unresolved`. Saída: lista de propostas `{article, source, book, provenance, score}` → relatório MD; `--apply` grava via `state`.
3. **Dedup (`kb/dedup.py`)** — candidatos: (a) grupos do manifest com mesma `source` e >1 artigo vivo; (b) pares do índice de embeddings com cosseno ≥ 0,95 **e** `SequenceMatcher.ratio ≥ 0,85` sobre corpo normalizado. Sobrevivente: path com topic > raiz; empate → mais palavras. Apply: `move_to_archive` (perdedor+summary), `mark_archived`, `update_index`+refresh.
4. **Topics (`kb/topics.py`)** — `normalize`: mapa fechado de variantes, regex in-place na linha `topic:`; `assign`: LLM (client.chat) com prompt fechado na taxonomia, resposta fora da lista → rejeitada no parse (nunca gravada); relatório com proposta+confiança; `--apply` grava aprovados.
5. **CLI** — sub-apps `manifest`, `dedup`, `topics`; dry-run é o default em tudo; `--commit` versiona no vault (origem+destino+manifest, padrão da 027).

## Condições binárias de risco (gate test-design)

| Condição | Presente? |
|---|---|
| Output estrutural estável | **sim** — manifest v2 |
| I/O em store real / migração | **sim** — manifest + frontmatter em lote |
| Output não-determinístico | **sim** — `topics assign` (LLM) → restrição dura + testes com mock |

## Riscos

- Manifest legado com paths absolutos: leitura tolerante + teste de compat.
- Embed on-demand dos ambíguos depende do servidor `:1234`: degrade para `unresolved` com aviso (nunca bloqueia o lote).
- Dedup engolir par temático: o critério dupla-chave (cosseno + ratio textual) é candidatura; o diff no relatório e o gate humano decidem.
- `KB_TOPICS` no lugar errado reverteria topics no próximo compile: entra no `.env` do engine com teste manual de `canonical_topic` no ambiente real (risco 4 do plano aprovado).

## Ordem

B1 → B2 → **B3 (HITL)** → B4 → **B5 (HITL)** → B6 → B7 → **B8 (HITL)**. B6/B7 podem adiantar em paralelo a B4/B5.
