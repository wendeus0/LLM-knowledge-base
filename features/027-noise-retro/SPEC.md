---
feature: 027-noise-retro
title: Noise scan retroativo sobre library/ e apply seguro
epic: lint
status: done
created: 2026-08-05
pr:
---

# Noise scan retroativo sobre library/ e apply seguro

## Objetivo

Hoje `kb noise scan` devolve 0 candidatos no vault real porque varre apenas `raw/books/*/metadata.json`, enquanto os 34 livros extraídos vivem em `library/<área>/<livro>/metadata.json`; deveria encontrar os ~105 capítulos-ruído e os artigos da wiki derivados deles, e o `apply` deveria arquivá-los de forma reversível e auditável.

## Requisitos funcionais

- [x] RF-01 [P1]: Dado um vault com `metadata.json` em `raw/books/*/` e/ou `library/*/*/`, quando `kb noise scan` rodar, então os capítulos de ambas as raízes são classificados pela taxonomia e os candidatos incluem os artigos da wiki cujo `source:` casa com capítulo-ruído.
- [x] RF-02 [P1]: Dado o scan, quando houver candidatos, então a saída lista cada um com livro de origem, título original do capítulo, categoria da taxonomia e path do artigo — informação suficiente para revisão humana sem abrir arquivo por arquivo.
- [x] RF-03 [P1]: Dado `kb noise apply`, quando executar, então cada artigo candidato é movido para `archive/` preservando a hierarquia relativa e com backup versionado em caso de colisão (semântica de `archive.move_to_archive`), nunca `unlink`, e capítulos-fonte de `library/` **não** são tocados.
- [x] RF-04 [P1]: Dado `kb noise apply --commit`, quando concluir, então o commit no git do vault registra origem (deleção em `wiki/`) e destino (novo path em `archive/`) — não apenas o destino.
- [x] RF-05 [P2]: Dado um apply com ao menos um move, quando concluir, então `_index.md` é regenerado e o índice de embeddings é atualizado, sem re-embedar artigos inalterados.
- [x] RF-06 [P2]: Dado um artigo candidato com summary espelho em `wiki/_summaries/`, quando o artigo for arquivado, então o summary é arquivado junto (mesma semântica de move).

## Requisitos técnicos

- Raízes de varredura derivadas de `DATA_DIR`: `raw/books/*/metadata.json` e `library/*/*/metadata.json`. Sem env var nova.
- Casamento artigo↔capítulo por `source:` basename (o casamento por título permanece; é inerte no vault real porque o compile reescreve títulos).
- `archive_candidates` de `kb/noise.py` é substituído pela semântica de `move_to_archive` (`kb/archive.py`) — hierarquia + backup versionado. Reconciliação V7 completa fica fora (feature 029).
- Sem `--dry-run` novo: `kb noise scan` é o dry-run.
- Manifest: fora desta feature (schema v2 e manutenção em archive são da 028). O apply desta feature não escreve manifest — os artigos-alvo não têm entrada hoje.

## Mudanças de API/CLI

- `kb noise scan`: mesma invocação, saída enriquecida (livro, capítulo, categoria, artigo). Sem breaking change de flags.
- `kb noise apply [--commit]`: mesmas flags; comportamento de move e commit corrigidos. Mudança de comportamento documentada: destino preserva hierarquia (antes achatava).
- `scan_corpus()` muda o tipo de retorno (lista de candidatos estruturados). Consumidor único é o CLI; testes ajustados.

## Testes

- Unit: scan multi-root (fixture com livro em `raw/books/` E em `library/`); contenção de path nas duas raízes; colisão de basename entre livros classificada consistentemente; saída estruturada com book/título/categoria; apply move com hierarquia + backup versionado em colisão; summary acompanha; capítulo-fonte intocado.
- Integration: vault temporário completo — scan encontra, apply move, commit registra origem+destino (asserção sobre `git status` do vault fixture), `_index.md` regenerado.
- Manual (lote A3, HITL): preflight no vault real → scan → relatório → aprovação do dono → apply --commit → conferir contagens e a home da plataforma.

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4h |
| Bloqueador | não |
| Risk | baixa — operações reversíveis, gate humano antes do lote real |

## Dependências

- Nenhuma feature; DOMAIN compartilhado em `features/027-noise-retro/DOMAIN.md`.

## Notas

Primeira das três features do esforço de higiene (plano aprovado 2026-08-05; ADR-0018 etapas 1–3). Valida a maquinaria relatório→aprovação→apply+commit que 028 e 029 reusam. O falso positivo residual conhecido (capítulo de conteúdo intitulado "Index") é absorvido pelo gate humano do relatório.
