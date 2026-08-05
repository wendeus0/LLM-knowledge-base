---
feature: 027-noise-retro
status: validated
validated_at: 2026-08-05
validated_by: orquestrador (Fable 5), premissas verificadas por exploração read-only + medição no vault real
---

# CONTRACT — 027-noise-retro

## Premissas técnicas verificadas

| # | Premissa | Verificação | Estado |
|---|---|---|---|
| 1 | O vault real tem os metadados em `library/` | `find ~/vault/library -name metadata.json` → 34; `raw/` → 0 | **confirmado** |
| 2 | A taxonomia default classifica ~105 capítulos de library como ruído | simulação da passada A sobre os 34 metadata.json (prefacio 29, indice 26, sobre_o_autor 10, capa 9, copyright 7, colofao 7, agradecimentos 6, dedicatoria 4, elogios 4, encerramento 3) | **confirmado** |
| 3 | O casamento por basename alcança os artigos | todos os 1.042 artigos têm `source:` basename; colisão entre livros é homogênea (slug embute o título; 32 casos medidos) | **confirmado** |
| 4 | `move_to_archive` é reutilizável pelo apply | assinatura `(candidates: list[dict{source,dest}], archive_dir, *, dry_run)` com contenção de dest e backup versionado (`kb/archive.py:133-194`) | **confirmado** |
| 5 | Commit de origem+destino é só passar os paths | `kb.git.commit` faz `git add <paths>`; `git add` de path deletado stage-a a deleção (`kb/git.py:63-69`) | **confirmado** |
| 6 | `_summary_path` dá o espelho do summary | `kb/compile.py:344-349` (não usar em modo leitura com side effect de mkdir — o apply calcula o espelho sem criar diretório) | **confirmado, com ressalva anotada** |
| 7 | Refresh de embeddings é incremental e barato | `refresh_embeddings_index` (`kb/embeddings.py:164`); build por hash/relpath descarta movidos sem re-embedar | **confirmado** |
| 8 | Sem corrida com jobs | `crontab -l` sem jobs do kb (verificado 2026-08-05) | **confirmado** |

## Premissas de produto (do DOMAIN, acordadas com o dono)

- Capítulos-fonte de `library/` nunca são arquivados; só artigos da wiki (+ summaries).
- Nenhum `unlink`; todo move com backup versionado; tag git antes do lote real.
- Lote real (T-003) só com relatório aprovado pelo dono.
- Manifest fora desta feature: pré-condição **validada em runtime** (nenhum dos 40 candidatos tinha entrada; as 5 entradas existentes são de artigos cybersecurity fora do lote) e o `apply` passou a avisar quando um candidato tem entrada. A manutenção real é B4 (028).

## Riscos aceitos

| Risco | Mitigação |
|---|---|
| Falso positivo de classificação por título ("Index" como capítulo de conteúdo) | Relatório book-qualified + gate humano |
| Mudança do retorno de `scan_corpus` quebra testes que fixam a estrutura antiga | Reescrita dos 4 testes de contenção prevista na SPEC |
| Servidor de embeddings fora do ar durante apply | Refresh degrada com aviso; move não aborta |

## Gate de TDD

1 condição binária de risco (output estrutural estável) → `test-design` com `test-red` como base: snapshot do candidato estruturado + propriedades do move (hierarquia, backup, summary junto, fonte intocada) + integração com git fixture.
