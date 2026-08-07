# Artigos de tema multi-fonte sob demanda (ADR-0018, decisão 2)

## Destination
O map fecha quando existe um primeiro artigo de tema real no vault: costurado de várias fontes, nascido no vault, conferido em tela renderizada. Não fecha em SPEC nem em ADR — fecha em artigo.

## Notes
Domínio: o compile atual é 1 documento → 1 artigo; a política aprovada quer artigo DE TEMA, multi-fonte, gerado sob demanda, nunca por job automático. O gate de qualidade deixou de ser min-refs e passou a ser "não perdeu informação", termo que o ADR não definiu.

Regra de casa: o compile de tema entra como FEATURE com pipeline completo desde o início (SPEC → PLAN → CONTRACT → RED → GREEN → gates). O map decide; a feature entrega. Regras herdadas vigentes: nenhum lote no vault sem relatório → aprovação do dono → apply com commit; nada de `unlink`; tag antes de lote destrutivo; afirmação sobre tela exige tela renderizada (Playwright ou URL rodando).

Leitura obrigatória em toda sessão: ADR-0018 (decisão 2 e gatilho de revisão de `_chapters/`) e as evidências E1–E12 abaixo, com suas citações de código.

## Decisions so far
- Destination fecha em artigo, não em SPEC — decisão do dono, fechada no charting.
- Compile de tema é feature com pipeline completo — protótipo throwaway não é caminho oficial; decisão do dono, fechada no charting.
- Tema piloto será escolhido por medição, não por preferência — decisão do dono, fechada no charting; a medição é ticket aberto (arquivo-filho).

## Evidence at charting
- E1. O compile lê UM arquivo de `raw/` e monta o prompt com esse único conteúdo mais metadados do próprio livro. Nada de busca, índice ou outro artigo entra no contexto do LLM (`kb/compile.py:404-474`, `kb/compile.py:288-294`).
- E2. A convenção `_*` é aplicada em `kb/fsutil.py:21-22`, `kb/search.py:25-26`, `kb/embeddings.py:62-63`, `kb/lexical_index.py:44`, `kb/graph.py:28`. `wiki/_chapters/` é inalcançável por qualquer retrieval hoje. Única exceção: `kb/api/articles.py:39-49` (fingerprint varre a wiki inteira).
- E3. Manifest: 856 entradas, 856 artigos distintos, zero artigos com mais de uma fonte. 1:1 por construção — `mark_compiled` grava uma fonte por entrada (`kb/state.py:88-108`), `upsert_knowledge` chaveia por fonte (`kb/state.py:232-258`).
- E4. Proveniência do manifest: 824 de 856 (96%) por `backfill-basename` — match de nome de arquivo. 19 por conteúdo, 13 por cosseno. Cadeia de desempate em `kb/backfill.py:81-115`; o que não desempata vira `unresolved`.
- E5. `library/`: 800 capítulos .md, mas 23 fontes ainda são PDF/EPUB não extraídos. A categoria `llm/` tem 10 binários e zero markdown. Só 34 dos 43 livros de `software-engineering/` têm `metadata.json`.
- E6. `library/` é lida apenas para proveniência (`kb/backfill.py:29`) e classificação de ruído (`kb/noise.py:215-217`). Nunca como corpus de busca. O pré-requisito "retrieval sobre library/" declarado pelo ADR não tem implementação.
- E7. Wiki viva: 345 artigos, sendo 214 `algorithms` + 89 `learning` + 42 no resto. Arquitetura, Python e testes estão todos em `_chapters/`.
- E8. `wiki/_chapters/`: 630 capítulos, 37 livros. Maior: *Release It!* com 138 capítulos; depois *API Design Patterns* 37, *Fluent Python* 30, *Working Effectively with Legacy Code* 28, *Observability Engineering* 26.
- E9. O frontmatter de capítulo tem `title/topic/tags/source`, mas não tem `book` — o livro é o diretório-pai.
- E10. Existe um perfil de retrieval chamado `article` em `kb/config.py:89` sem nenhum chamador no código.
- E11. `wiki/_sources/` tem 712 capítulos .md; é raiz de fontes do backfill e está fora de todos os corpora de busca.
- E12. O MAPA-DE-TEMAS.md de 2026-07-31 mediu clustering por cosseno: limiar 0,88 dá 116 grupos cobrindo 469 de 1.037 artigos (45%); a janela é estreita — em 0,85 o maior grupo salta de 31 para 148, em 0,82 vira um caroço de 637.
- E13. Cruzamento wiki viva × manifest medido no charting (2026-08-06): dos 345 artigos vivos, **225 têm proveniência** e **120 não têm** — são estes os `unresolved` (o REPORT da 029 registrou 124 no dia do lote; a contagem de hoje dá 120). O manifest ainda aponta para **631 artigos que já não estão vivos** — os que foram para `_chapters/`. Os 120 `unresolved` não são homogêneos: 88 estão em `learning`, 17 em `ai`, 7 em `algorithms` — e **7 são arquivos soltos na raiz da wiki, sem diretório de topic**, com títulos que os denunciam como capítulos de livro que escaparam do reagrupamento (`api-design-patterns-front-matter-e-visao-geral-da-obra.md`, `dentro-da-capa-topicos-de-design-de-apis.md`, `honeycomb.md`, `introducao-a-integracao-de-aplicacoes-com-mensageria.md`, `o-escopo-do-desafio.md`, `exercicios-de-algebra-linear-...`, `recursos-de-referencia-para-ciencia-de-dados-...`). São falha de proveniência visível a olho nu, e o insumo mais direto de [qualidade-da-proveniencia](008-qualidade-da-proveniencia.md).

## Not yet specified
Os 120 `unresolved` do backfill ainda não têm destino definido para quando o tema nascer — se entram como fonte elegível, se ficam de fora, se exigem rodada de desempate antes do piloto. A extração dos 23 binários da `library/` (incluindo a categoria `llm/` inteira, que não tem um markdown sequer) é trabalho real que o map pressente mas não consegue ticketar antes de se saber de onde a síntese lê. A reativação do min-refs (decisão 1 do ADR: "artigo raso é bug") paira sobre o gate novo: não está claro o que conta como referência real num artigo costurado de várias fontes, nem como os dois gates convivem. A mecânica de "livro novo marca o tema como stale" (decisão 4 do ADR) não está desenhada — nem detecção, nem superfície, nem re-compile. E há custo e latência de síntese por resolver: *Release It!* tem 138 capítulos e não cabe num prompt; qualquer destino realista passa por seleção ou redução de contexto que ainda não existe.

## Out of scope
- Detecção automática de lacuna (derrubada por medição, ADR item 5).
- Obsidian como leitor (ADR item 6).
- Compatibilidade multi-vault (feature 010 arquivada).
- Web aberta na rotina de ingestão (ADR item 4).
