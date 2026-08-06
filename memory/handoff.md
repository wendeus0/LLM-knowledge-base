# Handoff — 2026-08-06

Sessão fechou o esforço **ADR-0018 etapas 1–3** inteiro: features 027 (noise retroativo), 028 (proveniência + dedup + topics) e 029 (`_*` + reagrupamento), PRs #69/#70/#71 mergeados, `main` @ `52d1006`. Working tree limpo; vault com 6 tags de rollback e todos os lotes commitados.

## Estado do vault

345 artigos vivos (207 transcripts + 14 harness + 124 unresolved) · 630 capítulos em `_chapters/` por 37 livros · manifest com 856 entradas de proveniência · 10 trilhas canônicas · plataforma funcionando (conferida em tela após cada lote).

## Decisões do dono nesta sessão (não reabrir)

- Executar o ADR-0018 (não higiene stopgap); dedup só de ingestão; topics só frontmatter; relatório→aprovação em todo lote; move para `_chapters/` gated.
- Taxonomia: 10 canônicos (algorithms, ai, python, learning, cybersecurity, harness, software-architecture, data, testing, operations) + mapa de variantes.
- No gate final: transcripts-youtube e harness FICAM na wiki (não são livros).

## Para a próxima sessão

O próximo esforço é o **compile multi-fonte** (decisão 2 do ADR-0018) — abrir com wayfinder próprio. Insumos prontos: `MAPA-DE-TEMAS.md`, 55 gêmeos temáticos (`kb dedup scan`), 124 unresolved, proveniência completa. Pendências menores em `PENDING_LOG.md` (sessão 2026-08-05/06).

## Prompt de retomada

```
Leia memory/project_state.md e memory/next_steps.md. O ADR-0018 etapas 1-3
está completo em main (52d1006). Quero abrir o esforço do compile
multi-fonte — comece pelo wayfinder.
```
