# Salvar o insubstituível

Type: task
Status: open

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

<!-- preencher na resolução -->
