---
feature: 029-chapters-regroup
title: Convenção _* honrada em todo o engine e reagrupamento por livro
epic: infra
status: approved
created: 2026-08-06
pr:
---

# Convenção `_*` honrada em todo o engine e reagrupamento por livro

## Objetivo

Hoje sete pontos do engine ignoram a convenção `_*` (o heal pode deletar summary **hoje**; pós-move, `find_orphans` arrastaria `_chapters/` inteiro para `archive/`) e os 975 artigos de capítulo seguem misturados na wiki; ao final, `_*` é invisível para todo o engine, nenhuma remoção é `unlink`, e os capítulos estão agrupados por livro em `wiki/_chapters/` — com o move final executado apenas sob aprovação explícita do dono, ciente de que a wiki visível esvazia até o compile multi-fonte existir.

## Requisitos funcionais

- [ ] RF-01 [P1] (C1): Dado qualquer diretório `_*` ou `.*` sob `wiki/`, quando `lint`, `heal`, `archive` (órfãos e idade), `update_index` e `stats` rodarem, então nenhum arquivo dentro dele é listado, amostrado, indexado, contado ou marcado como candidato — mesma semântica já usada por search/embeddings/graph.
- [ ] RF-02 [P1] (C2): Dado um stub detectado pelo heal, quando a remoção executar, então o arquivo vai para `archive/` com a semântica de `move_to_archive` (hierarquia + backup versionado), nunca `unlink`; o manifest é atualizado (`mark_archived`).
- [ ] RF-03 [P1] (C3): Dado `kb regroup scan`, quando rodar, então agrupa os artigos vivos por livro via proveniência do manifest (com os `unresolved` listados como braço de decisão humana) e imprime o plano de move `wiki/<...> → wiki/_chapters/<livro>/`, sem alterar nada.
- [ ] RF-04 [P1] (C3): Dado `kb regroup apply --book <slug>`, quando executar, então move os artigos do livro (e seus summaries, para `wiki/_summaries/_chapters/<livro>/`) preservando o nome, atualiza `update_article_path` no manifest, regenera `_index.md`, refresca embeddings e commita **por livro**.
- [ ] RF-05 [P1] (C4): Dado o lote final, quando o dono aprovar explicitamente ("a wiki esvazia"), então os livros aprovados são movidos um a um, com tag git prévia e smoke de search/stats ao final; sem aprovação, nada se move.
- [ ] RF-06 [P2]: Dado um artigo `unresolved` (sem proveniência), quando o regroup rodar, então ele permanece na wiki e aparece no relatório como pendência humana — nunca é movido por inferência.

## Requisitos técnicos

- Helper único (`kb/fsutil.iter_articles(wiki_dir)` ou equivalente) com a semântica de `graph._e_artigo` (`_` e `.`), adotado nos sete pontos; sem mudança de assinatura pública dos comandos.
- `heal` mantém `--commit` e o registro de backup; a política de remoção única (move) fecha a dívida V7 no escopo do heal — a unificação do formato de backup do `.heal_backup` legado fica fora.
- Agrupamento pela chave `book` do manifest (materializada na 028); cosseno/`MAPA-DE-TEMAS.md` são insumo do relatório para temas transversais, não critério de move.
- Golden set e links do workspace `teach` quebram no move — perda aceita pelo ADR-0018, registrada no REPORT.
- Checar `claims.jsonl`/`knowledge.json` por referências a paths antes do C4; dangle aceito e registrado se houver.

## Mudanças de API/CLI

- Novo sub-app `regroup`: `kb regroup scan` e `kb regroup apply --book <slug> [--no-commit|--commit]`.
- `heal`: mudança de comportamento documentada (stub vai para `archive/` em vez de `unlink`).

## Testes

- Unit: `iter_articles` exclui `_*`/`.*`/symlink; cada adotante coberto (lint não lista, heal não sorteia, archive não marca, update_index não indexa, stats não conta artigo sob `_*`); heal move stub com backup e marca manifest; regroup agrupa por `book`, ignora `unresolved`, calcula destinos.
- Integration: vault fixture com manifest → `regroup scan` imprime plano; `apply --book` move artigo+summary, atualiza manifest, regenera índice, commita por livro (git fixture); artigo movido some de search/stats/_index.
- Manual (C4, HITL): preflight + tag → relatório de grupos → aprovação explícita do dono → apply livro a livro → `kb index build` + smoke + tela da plataforma.

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 8h |
| Bloqueador | não |
| Risk | média-alta — move em massa; mitigada por commit por livro, tags, manifest e gate final humano |

## Dependências

- 028 mergeada (PR #70): `manifest.book`, `mark_archived`, `update_article_path`.
- DOMAIN compartilhado: `features/027-noise-retro/DOMAIN.md`.

## Notas

Terceira e última feature do esforço (etapa 3 do ADR-0018). Estado do vault na abertura: 975 artigos vivos, 856 entradas de manifest (849 com proveniência, 126 `unresolved` fora), 10 topics canônicos.
