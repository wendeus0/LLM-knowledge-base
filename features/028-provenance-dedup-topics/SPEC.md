---
feature: 028-provenance-dedup-topics
title: Proveniência materializada, dedup de ingestão e topics reais
epic: infra
status: in_progress
created: 2026-08-05
pr:
---

# Proveniência materializada, dedup de ingestão e topics reais

## Objetivo

Hoje o `manifest.json` cobre 5 de 1.042 artigos, dois artigos do mesmo documento convivem na wiki e 497 artigos não têm topic utilizável; ao final, cada artigo terá proveniência auditável no manifest, duplicatas de ingestão estarão arquivadas e as trilhas da plataforma serão povoadas por topic real — tudo por lotes com relatório e aprovação do dono.

## Requisitos funcionais

- [x] RF-01 [P1] (B1): Dado o manifest, quando uma entrada for escrita ou lida, então ela suporta os campos `source` (relativo a `DATA_DIR`), `article` (relativo a `WIKI_DIR`), `book`, `provenance` (`compile|backfill-basename|backfill-content|backfill-cosine|unresolved`) e `status` (incluindo `archived`), preservando compatibilidade com as entradas e consumidores atuais (`find_compiled_entry` continua impedindo recompile de duplicar).
- [x] RF-02 [P1] (B2): Dado `kb manifest backfill`, quando rodar sem `--apply`, então produz relatório artigo→fonte com o método de pareamento por entrada (basename único → conteúdo idêntico → cosseno para ambíguos → `unresolved`), sem escrever nada; com `--apply`, materializa as entradas aprovadas.
- [x] RF-03 [P1] (B4): Dado um archive/move de artigo com entrada no manifest, quando executar, então a entrada é atualizada (`status: archived`, path novo) — nunca fica apontando para path inexistente.
- [x] RF-04 [P1] (B4): Dado `kb dedup scan`, quando rodar, então lista pares de duplicata de ingestão — mesma fonte no manifest, ou cosseno ≥ 0,95 com razão de similaridade textual normalizada ≥ 0,85 — com o diff resumido por par e o sobrevivente proposto (path com topic vence o da raiz); par temático (fontes distintas e similaridade textual abaixo do critério) nunca entra.
- [x] RF-05 [P1] (B5): Dado `kb dedup apply`, quando executar com a lista aprovada, então o perdedor e seu summary vão para `archive/` (semântica 027), o manifest é atualizado e `_index.md`/embeddings são refrescados.
- [x] RF-06 [P1] (B6): Dado `KB_TOPICS` configurado com a taxonomia fechada pelo dono, quando `kb topics normalize` rodar, então variantes do mapa aprovado (ex.: `geral`→`general`) são reescritas no frontmatter por edição in-place que preserva o resto do arquivo byte a byte.
- [x] RF-07 [P1] (B7): Dado `kb topics assign`, quando rodar sem `--apply`, então propõe topic para artigos `general`/sem topic da raiz usando o LLM restrito à taxonomia, em relatório; com `--apply`, grava só o frontmatter aprovado.
- [x] RF-08 [P2]: Dado qualquer comando novo, quando não houver `--apply`, então nada no vault é modificado (relatório é o dry-run).

## Requisitos técnicos

- Manifest continua lista JSON plana; entradas antigas seguem válidas (`provenance` ausente ⇒ `compile`). Paths novos gravados relativos; leitura tolera absolutos legados.
- Backfill sem braço LLM (decisão do plano): 63 ambíguos resolvem por cosseno entre embedding do artigo (índice existente) e embedding do capítulo candidato (servidor `:1234`); abaixo de 0,75, `unresolved`. 117 sem candidato ficam `unresolved` — viram braço humano no agrupamento (029).
- Similaridade textual do dedup: `difflib.SequenceMatcher.ratio()` sobre corpo normalizado (sem frontmatter, whitespace colapsado, casefold). Limiar 0,85 é **candidatura**, não veredito — o gate é o relatório com diff.
- `KB_TOPICS` vai no `.env` do engine (o `.env` do vault não existe; `canonical_topic` colapsaria tudo para `general`). Taxonomia proposta no relatório B6: os 6 reais do corpus + mapa de variantes; o dono fecha antes do assign.
- Edição de frontmatter por regex no padrão `heal._stamp_reviewed` + `atomic_write_text` — o serializer não faz round-trip fiel.
- Novos comandos em sub-apps `manifest`, `dedup`, `topics`; todos com `--apply` explícito e `--commit` para versionar no vault.

## Mudanças de API/CLI

- Novos: `kb manifest backfill [--apply] [--commit]`, `kb dedup scan`, `kb dedup apply [--commit]`, `kb topics normalize [--apply] [--commit]`, `kb topics assign [--apply] [--commit]`.
- `kb/state.py`: entrada estendida (aditiva); helper de manutenção `mark_archived`/`update_article_path` consumido pelo dedup (e pela 029 no move).
- Nenhuma mudança de comportamento em comandos existentes além de `noise apply` deixar de avisar quando a manutenção existir.

## Testes

- Unit: schema v2 round-trip + compat com entrada legada; `find_compiled_entry` não regride; matching por basename único/conteúdo idêntico/cosseno com fixtures de basename colidente; critério de dedup separa duplicata de ingestão de par temático; normalize preserva o arquivo fora da linha `topic:`; assign restrito à taxonomia (proposta fora da lista → rejeitada).
- Integration: backfill → manifest escrito → dedup scan encontra par plantado → apply arquiva perdedor+summary e atualiza manifest → `_index.md` sem o perdedor; tudo com git fixture confirmando commits por path.
- Manual (HITL): B3 (relatório de proveniência), B5 (dedup com diff por par), B6/B8 (taxonomia + topics) no vault real, cada um com aprovação do dono e contagens antes/depois; trilhas conferidas em tela após B8.

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 10h |
| Bloqueador | não |
| Risk | média — escreve manifest e frontmatter em lote; mitigada por dry-run default, HITL e git do vault |

## Dependências

- 027 mergeada (PR #69). DOMAIN compartilhado: `features/027-noise-retro/DOMAIN.md`.

## Notas

Números de referência do vault (pós-027): 980 artigos vivos; pareamento medido 857/1.037 por basename único+conteúdo, 63 ambíguos, 117 sem resolução; 59 pares ≥0,95 (antes dos lotes — recontar no B4). Reusa `scripts/measure_corpus_quality.py` (`source_candidates`, `duplicate_measurement`).
