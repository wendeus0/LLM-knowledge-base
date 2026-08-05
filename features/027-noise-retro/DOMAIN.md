# DOMAIN — Higiene do corpus (features 027/028/029)

> Produzido pelo grilling de 2026-08-05, que planejou as etapas 1–3 do ADR-0018. Este DOMAIN é compartilhado pelas três features do esforço; cada SPEC referencia a parte que executa. Feature 027 executa a etapa 1 (noise retroativo).

## Glossário

| Termo | Definição operacional |
|---|---|
| Paratexto | Capítulo sem conteúdo de conhecimento (dedicatória, sumário, índice remissivo, prefácio, copyright, capa, elogios, sobre o autor) — a taxonomia de `kb/noise.py` é a lista fechada. Conclusão é conteúdo, nunca paratexto |
| Artigo de capítulo | Artigo da wiki derivado 1:1 de um capítulo de livro; 1.037 dos 1.042 atuais |
| Duplicata de ingestão | Dois artigos derivados do mesmo documento-fonte (mesma fonte via manifest, ou conteúdo quase idêntico por critério operacional) — distinta de par temático |
| Par temático | Dois artigos próximos por cosseno mas de fontes distintas; NÃO é dedup — resolve-se no reagrupamento (ADR-0018) |
| Proveniência | Ligação artigo → arquivo-fonte materializada no `manifest.json`; hoje só 5 entradas existem |
| Backfill | Reconstrução retroativa da proveniência: basename único → conteúdo idêntico → cosseno → `unresolved` |
| Sobrevivente | No dedup, o artigo que fica; regra: o de path com topic vence o da raiz |
| Move | `shutil.move`/`git mv` com backup versionado — nunca `unlink`. Única política de remoção deste esforço |
| Lote HITL | Operação no vault que só executa após relatório revisado e aprovação explícita do dono |
| `_chapters/` | Destino dos artigos de capítulo no reagrupamento; invisível ao índice pela convenção `_*` (após C1 fechar os 7 furos) |

## Entidades e relações

- **Livro** (`library/<área>/<slug>/` + `metadata.json`) 1—N **Capítulo** (`NN-slug.md`)
- **Capítulo** 1—0..1 **Artigo** (`wiki/**.md`, frontmatter `source:` com basename)
- **Artigo** 1—0..1 **Summary** (`wiki/_summaries/<espelho>.md`) — summary acompanha o artigo em qualquer move
- **Manifest** N entradas, uma por fonte compilada — chave `source`, campos `article`, `book`, `provenance`, `status`

## Invariantes

1. Nenhuma remoção é `unlink`: todo lote é move com backup versionado, precedido de tag git no vault.
2. Capítulo-fonte de `library/` nunca é arquivado — só artigos da wiki. `metadata.json` permanece íntegro.
3. Lote destrutivo no vault exige: relatório → aprovação do dono → apply → commit no git do vault.
4. O manifest acompanha qualquer archive/move (status `archived`, path atualizado) — o guard de recompile (`find_compiled_entry`) nunca fica cego.
5. Dedup remove apenas duplicata de ingestão; par temático é intocável até o reagrupamento.
6. `rel_slug` de artigo vivo não muda nesta fase (topic é só frontmatter).
7. Após qualquer apply: `update_index` + refresh de embeddings, e contagens antes/depois conferidas.

## Decisões fechadas (com o dono, 2026-08-05)

| Decisão | Motivo |
|---|---|
| Finalidade: executar o ADR-0018, não higiene stopgap | Escolha explícita entre as duas |
| Dedup só de ingestão | Respeita o veto do ADR a "V5 isolado" |
| Topic: só frontmatter, arquivo parado | Mover muda slug e órfãna estudo |
| Relatório → aprovação → apply em todo lote | Detectores já erraram 2× neste repo |
| Vai até o agrupamento por livro; move para `_chapters/` é o último passo, gated | Dono ciente de que a wiki esvazia até o compile multi-fonte |

## Decisões assumidas pelo executor (reversíveis na SPEC)

- Capítulos-fonte ficam (invariante 2).
- Summaries acompanham o artigo (dedup e move).
- Taxonomia de topics fecha no primeiro relatório da feature 028, não em chat.

## Questões abertas (spec-clarify futuro / relatórios)

1. Taxonomia canônica de topics e o mapa de variantes (ddd/architecture/tensorflow → ?) — fecha no relatório B6.
2. Critério operacional de "quase idêntico" no dedup (igualdade pós-normalização vs limiar de diff) — fecha na SPEC da 028.
3. Destino de `claims.jsonl`/`knowledge.json` que referenciem paths movidos — checar antes do C4.
4. Summary de capítulo no move: espelho em `_summaries/_chapters/` (assumido) ou descarte — confirmar na SPEC da 029.

## Stakeholders

- **Decide:** o dono do vault (aprova cada lote; gate final do C4).
- **Consome:** a plataforma de estudos (trilhas, home) e o retrieval do `kb`.
- **Opera:** o executor (Claude), via CLI do kb com commit no git do vault.

## Critérios de sucesso

- `kb noise scan` encontra os capítulos-ruído de `library/` (hoje: 0; esperado: ~105 capítulos, ~66 artigos).
- Home da plataforma sem o par OWASP duplicado (tela renderizada como prova).
- Manifest cobrindo ≥ 82% dos artigos com proveniência auditável (`provenance` por entrada).
- Trilhas da plataforma povoadas por topic real (após B8).
- Zero `unlink` em qualquer lote; toda operação reversível por git.
