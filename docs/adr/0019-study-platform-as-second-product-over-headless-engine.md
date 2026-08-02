# ADR-0019 — A plataforma de estudos é um segundo produto sobre a engine headless

**Status:** aceito
**Data:** 2026-08-02
**Contexto da decisão:** grilling de 2026-08-01/02, registrado em `docs/research/2026-08-01-kb-para-estudo/`

## Contexto

O `kb` nasceu como engine de knowledge base operada por CLI: ingere, compila, busca, responde. O consumo do resultado sempre foi terceirizado — na prática, o Obsidian lendo `<KB_DATA_DIR>/wiki`.

Essa divisão parou de servir. O usuário passou dois dias corrigindo a engine sem conseguir usá-la para o que queria (estudar cibersegurança), e o grilling revelou que ele não precisa de um leitor melhor: precisa de **plataforma de estudos** — flashcards, revisão espaçada, calendário, trilha — que o Obsidian não é e não vai ser.

Isso impõe duas decisões arquiteturais duráveis que nenhum ADR anterior cobre: **como o consumo alcança a engine** e **onde vive o estado que não é corpus**.

## Decisão

### 1. O `kb` permanece headless; a plataforma é um segundo produto no mesmo repositório

`kb/` continua sendo engine sem tela. A plataforma vive em `study/` e consome a engine por uma API HTTP local (`kb/api/`), não por import direto das telas.

Monorepo porque o mantenedor é solo: repositório separado obrigaria API estável desde o primeiro dia e duplicaria CI, versionamento e deploy. Mesmo assim, a fronteira HTTP é real — a plataforma não importa `kb.search` de dentro de um template.

### 2. O corpus é território exclusivo da engine; o estado de estudo é território exclusivo da plataforma

A plataforma **não escreve em `wiki/`**. Nota, destaque, flashcard, revisão e progresso vivem em SQLite próprio, chaveados por `rel_slug`.

Esta é a decisão que resolve o conflito estrutural: `compile` e `heal` reescrevem artigos por desenho, e o `AGENTS.md` já proibia edição manual da wiki. Uma plataforma que editasse o artigo teria a edição apagada no próximo `heal`. Separando as camadas, o conflito **deixa de existir por construção** em vez de ser mediado por trava, flag ou merge.

### 3. `rel_slug` é a identidade pública de artigo

`ai/transformers` — path relativo à wiki, sem extensão. Atravessa HTTP, URL, template e banco. `Path` nunca é serializado; `stem` nunca é identidade.

O vault tem 4 stems duplicados, e antes da correção de identidade a resolução dependia da ordem do `rglob`, que o sistema de arquivos não garante. Uma plataforma web sobre isso teria URL apontando para um artigo e wikilink para outro.

## Consequências

**A favor**

- A engine ganha uma superfície testável que a CLI não dava, e que serve a qualquer consumidor futuro.
- O trabalho de retrieval, grounding e compile vira backend em vez de virar dívida — nada se joga fora.
- O estado de estudo é versionável e restaurável independentemente do corpus.

**Contra**

- O repositório deixa de ser "só engine". `CLAUDE.md` e `AGENTS.md` precisam declarar as duas camadas, ou o próximo leitor assume o modelo antigo.
- Duas persistências convivem: `kb_state/` (corpus) e o banco da plataforma (estudo). Backup e migração passam a ter dois alvos.
- A API HTTP vira contrato a manter. Enquanto for localhost sem auth, o custo é baixo; expor à rede muda a conta e exige ADR próprio.

**Riscos aceitos**

- `kb_state/*.json` não tem locking (exceto `discovery`). Plataforma web e CLI escrevendo em paralelo é corrida real. Mitigação nesta fase: a plataforma **não escreve** em `kb_state/` — só lê. Se um dia precisar escrever, o locking vem antes.
- O destaque ancora em texto que a engine pode reescrever. Resolvido por política, não por trava: âncora perdida vira destaque `órfão` listado à parte, nunca apagado nem reposicionado por aproximação.

## Alternativas descartadas

**Plugin do Obsidian.** Traria a busca do `kb` e o Q&A para dentro do que já existe, a uma fração do custo. Descartado por decisão explícita do usuário: o destino é plataforma própria, e o plugin seria trabalho jogado fora.

**Forkar um front OSS** (Quartz, SilverBullet, WebObsidian). A varredura de licenças em `docs/research/2026-08-01-kb-para-estudo/frontends-oss.md` encontrou candidatos bons — mas todos são ferramentas de *notas*. Flashcard, calendário e trilha não são isso; a forma do produto é outra, e adaptar custaria mais que construir reusando bibliotecas (`fsrs`, `markdown-it-py`, `cytoscape`).

**Importar a engine direto no app, sem HTTP.** Mais simples no começo e mais rápido. Descartado porque apagaria a fronteira que torna a engine reusável, e porque a API já é necessária de qualquer forma — foi identificada na pesquisa como "o único código de verdade a escrever" independentemente do front escolhido.

## Gatilhos de revisão

- A plataforma precisar sair de localhost (auth, HTTPS e exposição mudam o modelo de ameaça).
- A plataforma precisar **escrever** em `kb_state/` (exige locking antes).
- Um terceiro consumidor aparecer para a API HTTP (a estabilidade do contrato deixa de ser opcional).
- O monorepo começar a atrapalhar: suíte lenta, CI acoplado, ou versionamento da engine travado pela plataforma.
