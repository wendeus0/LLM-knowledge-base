# Salvar o insubstituível

Type: task
Status: resolved (2026-07-31)

## Question

Duas coisas neste vault sustentam qualquer decisão deste map e nenhuma das duas está protegida. O que se protege, onde, e sob qual política?

**O golden set de 152 casos** — `~/vault/kb_state/bench/golden.json`, 31.611 B. É o único instrumento que mede retrieval no kb; todos os números do ADR-0017 saíram dele. Os 50 casos curados são trabalho manual e estão declarados **não reconstruíveis** em `memory/next_steps.md:11` e `memory/handoff.md:33`. Hoje está rastreado no git do vault — que tem **um único commit** (`0160552`) e nenhum remote verificado. É o P1 aberto do projeto.

**As 869 fontes de `library/`** — 185 MB, e o `.gitignore` do vault as exclui. É o único lugar onde o material bruto existe: `raw/` está vazia, e `wiki/_sources/` guarda 712 arquivos derivados, não os originais (17 PDFs, 6 EPUBs, 1 MOBI). Sem elas, a opção "recompilar" do ticket 006 deixa de existir — não há de onde recompilar.

Decidir isso primeiro não é zelo: os tickets 003 e 006 discutem medir e possivelmente descartar/reprocessar o corpus, e nenhuma dessas conversas é honesta enquanto uma falha de disco apaga a única cópia.

Pontos a resolver:

- O golden fica no vault (onde é usado) ou no repo da engine (onde é versionado com CI)? O map anterior levantou a tensão e não decidiu.
- `library/` entra em git-lfs, backup externo, ou fica declaradamente descartável — e se for descartável, o ticket 006 perde uma opção.
- O que é reconstruível a qualquer custo vs. o que não é: `embeddings.json` (141 MB) é reconstruível em 4m32; `topics/` e `_summaries/` são derivados; `learnings.json` tem 9 entradas triviais.

## Answer

Resolvido em 2026-07-31: **tudo vai para um único remote privado** — `github.com/wendeus0/kb-vault` — com `library/` dentro do git e binários via git-lfs.

**O que foi feito, verificável:**

- `git-lfs` 3.7.1 instalado; `.gitattributes` do vault trackeia `library/**/*.{pdf,epub,mobi}` — 24 objetos LFS (17 PDF, 6 EPUB, 1 MOBI), 161 MB.
- `library/` removida do `.gitignore` do vault; commit com 880 arquivos (as 863 fontes reais — 869 menos 6 `.DS_Store` — mais `manifest.json`/`knowledge.json`/`claims.jsonl`/`audit.jsonl` materializados pela travessia do ticket 002, e os 2 artigos de dorking).
- `gh repo create wendeus0/kb-vault --private --source ~/vault --push` — push completo, LFS 24/24.
- **Restauração provada por clone limpo** (`--depth 1` em diretório temporário): `golden.json` presente com **152 casos** parseáveis; 863 arquivos em `library/`; PDF amostrado é documento real de 18 MB, não pointer LFS.

**Decisões dos pontos abertos:**

- **O golden fica no vault** (`kb_state/bench/golden.json`), onde é usado — agora versionado com remote. A cópia no repo da engine ficou desnecessária: o risco era ausência de remote, não o lugar.
- **`library/` é insubstituível e está no git** (LFS para binários). A opção "recompilar" do ticket 006 permanece disponível.
- **Reconstruível permanece fora do git**, como já estava: `kb_state/embeddings.json` (141 MB, reconstrói em 4m32 via `kb index build`) e `tracking.db` (telemetria). `topics/` e `_summaries/` são derivados mas baratos e pequenos — seguem versionados por simplicidade.

**Política de backup resultante:** um `git push` no vault protege tudo que não se reconstrói. Gatilho de revisão: se a library crescer a ponto de estourar quota LFS do GitHub (armazenamento 10 GB no plano atual), reavaliar binários para storage externo.
