# REPORT — 029-chapters-regroup

**Estado:** `DONE_WITH_CONCERNS`
**Branch:** `feat/029-chapters-regroup`

## Contexto

Terceira e última feature do esforço de higiene (etapa 3 do ADR-0018). Antes dela: sete pontos do engine ignoravam a convenção `_*` (o heal podia deletar summary hoje), o heal era a última remoção destrutiva (`unlink`), e os 975 artigos de capítulo seguiam misturados na wiki visível.

## Mudanças (engine)

- **C1 — `kb/fsutil.iter_articles`**: semântica única de artigo vivo (`_*`, `.*`, symlink fora), adotada por lint, heal, archive (órfãos e idade), `update_index` e stats. Fecha o bug latente do heal sobre `_summaries` e o cenário em que `find_orphans` arrastaria `_chapters/` inteiro para `archive/`.
- **C2 — heal sem unlink** (V7 mínimo): stub vai para `archive/` com hierarquia e backup versionado; manifest marcado `archived`. A unificação do formato do `.heal_backup` legado fica como dívida registrada.
- **C3 — `kb regroup scan|apply --book`**: plano por proveniência do manifest (nunca cosseno), slug sanitizado por livro, summaries espelhados, `unresolved` jamais movido por inferência, commit por livro via `move_to_archive` com raiz de contenção em `_chapters/`.

## Lote final (C4, gate explícito do dono)

Decisão do dono em 2026-08-06: **mover 37 livros (630 artigos); `transcripts-youtube` (207) e `harness` (14) ficam** — não são livros, e com os 124 `unresolved` a plataforma mantém ~345 artigos visíveis até o compile multi-fonte.

Executado em 2026-08-06: **37 livros, 630 artigos + summaries movidos, 37 commits** (um por livro), zero erros, tag `pre-regroup-2026-08-06`. Vault final: **345 artigos vivos** (207 transcripts + 14 harness + 124 unresolved — soma exata), 630 em `_chapters/`. Smoke: índice em 345/345 artigos (2.666 chunks), `kb search` e `kb stats` respondendo, plataforma com home povoada e artigo vivo abrindo (tela conferida).

## Incidente do ciclo (registrado, não escondido)

O RED do C2 expôs a **terceira ocorrência do dia** da mesma classe: teste sem isolamento moveu stubs de fixture para o `archive/` do vault real e regenerou o `_index.md` real. Limpeza aprovada pelo dono; fix estrutural: o piso autouse do conftest agora cobre `ARCHIVE_DIR` e `kb.compile.WIKI_DIR`, como cobre `STATE_DIR` desde 2026-07-29.

## Validação

**1.042 passed** (13 testes novos de fsutil/regroup + reescritas de heal), ruff limpo, appeasement exit 0, cobertura 93%.

## Riscos e dívida

| Item | Estado |
|---|---|
| 28 menções a paths `wiki/` em `claims.jsonl`/`knowledge.json` dangling pós-move | Aceito pelo ADR; jobs decay/contradiction não instalados |
| Golden set do bench sem objeto (851 slugs referenciados) | Aceito pelo ADR; golden preservado em disco |
| `.heal_backup` legado com formato próprio | Dívida registrada (V7 completo) |
| `transcripts-youtube`/`harness` seguem como artigo de capítulo | Decisão do dono; reavaliar quando o compile multi-fonte definir o que é tema |

## Próximos passos

O esforço do ADR-0018 (etapas 1–3) fecha aqui. O próximo é o **compile multi-fonte** (pré-requisitos agora existem: proveniência materializada, `library/` íntegra, `_chapters/` populado) — esforço novo, com wayfinder/spec próprio.
