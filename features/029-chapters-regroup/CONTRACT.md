---
feature: 029-chapters-regroup
status: validated
validated_at: 2026-08-06
validated_by: orquestrador (Fable 5); premissas da exploração de 2026-08-05 reconferidas contra main pós-#70
---

# CONTRACT — 029-chapters-regroup

## Premissas técnicas verificadas

| # | Premissa | Verificação | Estado |
|---|---|---|---|
| 1 | Os 7 furos de `_*` existem e são os únicos | exploração 2026-08-05: `lint.py:33,53`, `heal.py:85-89`, `archive.py:44-45,72`, `compile.py:592-593`, `stats.py:4-8`; honram: search, embeddings, lexical, graph, api | **confirmado** |
| 2 | heal pode tocar `_summaries` hoje | `heal.py:85-89` exclui só `_index.md` e `.heal_backup`; 1.027 summaries elegíveis ao sorteio | **confirmado — bug latente que C1 corrige** |
| 3 | `manifest.book` existe para agrupar | 028 materializou 849 ligações com `book`; 126 `unresolved` fora | **confirmado** |
| 4 | Manutenção de manifest em move existe | `update_article_path`/`mark_archived` (028 B1/B4) com testes | **confirmado** |
| 5 | Mover arquivo não exige re-embedar | build por hash/relpath descarta e re-adota; `_chapters/` fica invisível após C1 | **confirmado** |
| 6 | Sem cron do kb | `crontab -l` reverificado 2026-08-05 | **confirmado** |
| 7 | `find_orphans` marcaria os 975 pós-move | 973/975 sem backlink (medição do ADR) — C1 antes de C4 é hard gate | **confirmado** |

## Premissas de produto

- Move para `_chapters/` SÓ com aprovação explícita do dono no C4, ciente de que a wiki visível esvazia (~5 artigos + unresolved) até o compile multi-fonte.
- `unresolved` nunca é movido por inferência — permanece na wiki como pendência humana.
- Commit por livro; tag antes do lote; tudo move, nunca unlink.
- Golden set preservado em disco; perda de retrievability aceita pelo ADR-0018 e registrada.

## Riscos aceitos

| Risco | Mitigação |
|---|---|
| Move em massa com path novo quebra wikilinks qualificados dos unresolved que ficam | Relatório do C4 lista; wikilink por stem continua resolvendo via graph (stem inalterado) |
| Nome de livro sujo (sufixos de fonte) vira slug ruim | Sanitização com teste; relatório mostra o slug antes do apply |
| Bench sem objeto pós-move | Aceito; registrado no REPORT |

## Gate de TDD

2 condições binárias de risco (I/O em store real; output estrutural do plano de move) → `test-design` com `test-red` base; cada módulo adotante do C1 tem teste próprio de exclusão.
