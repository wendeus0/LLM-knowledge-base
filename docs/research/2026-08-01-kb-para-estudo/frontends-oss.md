# Front-ends OSS para ler um vault markdown local

Pesquisa read-only. Data: 2026-08-01.

**Método.** Licença, estrelas, último push e flag de arquivamento vieram da API do GitHub (`gh api repos/<owner>/<repo>`), não de READMEs nem de listicles. Onde a API devolveu `NOASSERTION` (licença que o detector do GitHub não reconhece), o arquivo `LICENSE` foi baixado e lido. Descrições de funcionalidade vieram de README/estrutura do próprio repositório; conteúdo de blogs e agregadores foi tratado como pista para achar candidatos, nunca como fato.

---

## 1. Rowboat — veredito

**Não serve.** Não é um leitor de wiki markdown, e nem é web.

| campo | valor |
|---|---|
| licença | **Apache-2.0** — verificado no arquivo `LICENSE`, texto padrão íntegro, sem cláusula adicional. Permissiva. |
| o que é | `rowboatlabs/rowboat` — descrição oficial: *"A desktop AI coworker with a memory of your work and built-in surfaces to act on it."* Y Combinator S24. |
| entrega real | App **desktop Electron**. `apps/x/` é um workspace pnpm com `apps/main`, `apps/preload`, `apps/renderer` — arquitetura Electron clássica. `build-electron.sh` na raiz. |
| stack front-end | React + Vite (dev server em :5173), Radix UI, Tailwind v4, TipTap (editor WYSIWYG), CodeMirror 6, xterm.js (terminal embutido), SDK `ai`. |
| funcionalidade | Cliente de e-mail, note-taker de reuniões (mic + speaker, transcrição ao vivo), browser isolado embutido, "code mode" que chama Claude Code/Codex, agentes de background por evento/cron, MCP, Composio. |
| relação com markdown | Existe, mas ao contrário do que você quer: o Rowboat **gera** um vault markdown local ("*All data is stored locally as plain Markdown*") indexando **e-mail, reuniões, Slack e conversas com o assistente** em um "Obsidian-style backlinked knowledge graph". A fonte é a vida digital dele, não uma pasta que você aponta. |
| estrelas / atividade | 16.930 estrelas · push em 2026-07-31 · vivo, bem ativo |

**Por que você provavelmente reparou nele:** o README fala em "knowledge graph backlinkado estilo Obsidian" e "tudo em Markdown local". As palavras batem com o seu caso; o produto não. O Rowboat é um **agente de trabalho** que produz notas como efeito colateral. Você tem o problema inverso — já tem 1.040 artigos e quer **lê-los**.

O que dele seria aproveitável, na prática: a licença é boa (Apache-2.0) e o renderer é React+Vite. Mas o renderer conversa com o processo main por IPC via `@x/preload` e depende de `packages/core`. Extrair a UI significaria arrancar a ponte Electron inteira e reimplementar o backend. É o caminho mais caro da lista, para chegar num lugar pior que qualquer alternativa abaixo. **Descarte.**

---

## 2. Tabela comparativa

Legenda de licença: 🟢 permissiva · 🔴 copyleft (ver nota após a tabela) · ⛔ não é open source

| projeto | licença (lida do LICENSE) | stack front-end | lê markdown do disco? | `[[wikilinks]]` + frontmatter YAML | busca | graph view | atividade (push · estrelas) | reaproveitável? |
|---|---|---|---|---|---|---|---|---|
| **Quartz v5** `jackyzha0/quartz` | 🟢 **MIT** (`LICENSE.txt`) | Preact + esbuild, **SSG** → HTML estático + JS de ilha | **Sim** — lê `content/`, glob no diretório | **Sim, nativo** — `@quartz-community/obsidian-flavored-markdown` + `crawl-links` + `note-properties` | Sim, **client-side** (índice pré-buildado, `@quartz-community/search`) | **Sim** (`@quartz-community/graph`, d3-force) | 2026-07-30 · 12.913 | **Sim, o melhor** — v5 é modularizado em ~45 pacotes npm MIT independentes; trocar/adicionar plugin é contido |
| **WebObsidian** `xnohat/webobsidian` | 🟢 **MIT** | React + Zustand + CodeMirror 6 + unified/remark; **SPA + servidor Node** | **Sim** — aponta `VAULT_HOST_PATH` para a pasta, sem banco (config em `settings.json`) | **Sim** — wikilinks, embeds `![[x]]`, tags, callouts, KaTeX, Mermaid | Sim, **server-side** ("QMD": full-text + campos `tag:`/`path:`/`title:`, índice incremental persistido) | **Sim** (d3-force + pixi.js) | 2026-06-27 · 220 | **Sim, funcionalmente** — split `server/` + `web/` limpo, REST em `/api/v1`. **Mas:** 1 contribuidor real (59 commits), projeto jovem, provavelmente escrito por IA (tem `CLAUDE.md`, `PRD.md`, `IMPLEMENTATION_PLAN.md`). Risco de maturidade. |
| **Perlite** `secure-77/Perlite` | 🟢 **MIT** | **PHP** + JS, renderiza server-side; Docker | **Sim** — "coloque o vault inteiro no web dir, a página se constrói sozinha" | **Sim** — links, tags, imagens, preview no estilo Obsidian; suporta temas do Obsidian | Sim | **Sim**, interativo | 2026-01-21 · 1.968 | **Parcial** — funciona quase out-of-the-box como leitor, mas é PHP: fora da sua stack, e "refatorar e adaptar" para plugar no `kb` (Python) é atravessado |
| **SilverBullet** `silverbulletmd/silverbullet` | 🟢 **MIT** (`LICENSE.md`) | Cliente TS + CodeMirror 6 + Preact + esbuild; **servidor em Rust** | **Sim** — "Space" = coleção de páginas markdown, servida por uma HTTP API de arquivos | **Sim** — wikilinks bidirecionais, objetos indexados a partir de frontmatter, query language (SLIQ) | Sim | **Não** (tem backlinks e queries, não grafo) | 2026-08-01 · 5.752 | **Parcial, mas arquitetura elegante** — o cliente fala com o servidor por uma *file/space HTTP API* documentada. Esse é um seam real: dava para implementar essa API em Python sobre o seu vault. Contra: é um **editor** programável em Lua, não um leitor; peso alto para o que você quer |
| **memos** `usememos/memos` | 🟢 **MIT** | Go (backend) + React + Tailwind (`web/src`), API protobuf/connect-rpc | **Não** — SQLite/MySQL/Postgres, com migrations versionadas | Não | Sim (no banco) | Não | 2026-07-30 · 61.938 | **Não** — modelo de dados errado (microblog de notas curtas). Front bonito, mas acoplado a protobuf e a um domínio que não é o seu |
| **Foam** `foambubble/foam` | 🟢 **MIT** (grafia "Licence" confunde o detector do GitHub) | **Extensão do VS Code** | Sim (é o workspace do VS Code) | Sim | Sim (do VS Code) | Sim (comando `Foam: Show Graph`) | 2026-07-26 · 17.317 | **Não** — não existe front-end web. Publicar na web exige um SSG separado |
| **Dendron** `dendronhq/dendron` | 🟢 Apache-2.0 | **Extensão do VS Code** | Sim | Sim (hierarquia por ponto) | Sim | Sim | 2025-11-13 · 7.459 | **Não** — README declara: *"Dendron is currently in maintenance only, active development has ceased."* Morto |
| **Athens Research** `athensresearch/athens` | 🟢 EPL-1.0 (copyleft **fraco**, por arquivo) | Clojure/ClojureScript + re-frame | Não (DataScript próprio) | Parcial | Sim | Sim | **2023-02-03** · 6.298 | **Não** — README: *"Athens is no longer maintained."* Morto há 3 anos |
| **Logseq** `logseq/logseq` | 🔴 **AGPL-3.0** | ClojureScript + DataScript; Electron | Sim (versão file-based), mas a "DB version" migra para SQLite | Sim | Sim | Sim | 2026-07-31 · 44.198 | **Não** — AGPL + ClojureScript + DataScript. Monolito acoplado ao próprio motor de dados. A nova DB version está em beta com aviso explícito de *"data loss is possible"* |
| **Trilium** `TriliumNext/Trilium` | 🔴 **AGPL-3.0** | TypeScript | **Não** — banco SQLite próprio, notas importadas | Não (link próprio) | Sim | Sim | 2026-08-02 · 37.192 | **Não** — AGPL e não lê pasta markdown |
| **SiYuan** `siyuan-note/siyuan` | 🔴 **AGPL-3.0** | TypeScript + Go | Não (block DB própria) | Parcial | Sim | Sim | 2026-08-02 · 45.565 | **Não** — AGPL, block-based |
| **AppFlowy** `AppFlowy-IO/AppFlowy` | 🔴 **AGPL-3.0** | **Flutter** + Rust | Não | Não | Sim | Não | 2026-07-24 · 74.751 | **Não** — AGPL, Flutter, dados em banco próprio |
| **Notesnook** `streetwriters/notesnook` | 🔴 **GPL-3.0** | TypeScript/React | Não (E2EE, backend próprio) | Não | Sim | Não | 2026-08-01 · 14.349 | **Não** — GPL + criptografia fim-a-fim é o oposto de "ler um vault local" |
| **mdSilo** `mdSilo/mdSilo-app` | 🔴 **AGPL-3.0** | Tauri + TypeScript | Sim | Parcial | Sim | Sim | 2026-03-25 · 850 | **Não** — AGPL, projeto pequeno e desacelerando |
| **Anytype** `anyproto/anytype-ts` | ⛔ **"Any Source Available License 1.0"** — **não é open source**. Permite uso, modificação e redistribuição apenas *(a) for Non-Commercial Use, or (b) for Commercial Use in Allowed Networks* | Electron + TS | Não (objetos próprios, P2P) | Não | Sim | Sim | 2026-08-01 · 8.535 | **Não** — licença restritiva com trava de rede. Descarte imediato |
| **Flowershow** `flowershow/flowershow` | 🔴 **AGPL-3.0** | Next.js + TS | Sim | Sim | Sim | Parcial | 2026-08-01 · 1.097 | **Não pela licença** — seria um bom candidato técnico (Next.js publicando markdown/wiki), mas é AGPL |
| **Emanote** `srid/emanote` | 🔴 **AGPL-3.0** (LICENSE é o texto AGPLv3) | **Haskell** + hot-reload | Sim | Sim | Sim | Sim | 2026-07-26 · 954 | **Não** — AGPL e Haskell |
| **obsidian-html** `obsidian-html/obsidian-html` | 🔴 **GPL-3.0** | Python → HTML estático | Sim | Sim | Parcial | Sim | 2025-07-12 · 383 | **Não** — GPL, e parado há ~1 ano |
| **Khoj** `khoj-ai/khoj` | 🔴 **AGPL-3.0** | Python + Next.js | Sim (indexa markdown) | Parcial | Sim (semântica) | Não | 2026-08-02 · 36.152 | **Não** — AGPL; e é busca com IA, não interface de leitura |
| **Wiki.js** `requarks/wiki` | 🔴 **AGPL-3.0** | Vue | Não (Postgres) | Não | Sim | Não | 2026-08-01 · 28.691 | **Não** |
| **Reor** `reorproject/reor` | 🔴 **AGPL-3.0** | Electron/JS | Sim | Parcial | Sim (vetorial) | Sim | 2025-05-13 · 8.577 · **arquivado** | **Não** — arquivado |
| **zk** `zk-org/zk` | 🔴 **GPL-3.0** | Go, **CLI** | Sim | Sim | Sim | Não | 2026-07-30 · 2.739 | **Não** — não tem front-end |
| **obsidian-digital-garden** `oleeskild/obsidian-digital-garden` (+ template `oleeskild/digitalgarden`) | 🟢 **MIT** (ambos) | Next.js (o template) | Via plugin do Obsidian, que **publica** as notas | Sim | Sim | Sim | 2026-07-30 · 2.441 | **Parcial** — o modelo é "publicar do Obsidian pro Vercel". Você teria que contornar o plugin e alimentar o template direto |
| **digital-garden-jekyll-template** `maximevaillancourt/...` | 🟢 **MIT** | Jekyll (Ruby) | Sim | Sim | Sim | Sim | 2025-12-01 · 1.278 · **arquivado** | **Não** — arquivado, e Ruby |
| **Astro Starlight** `withastro/starlight` | 🟢 **MIT** | Astro, SSG | Sim | **Não nativo** (precisa de plugin de terceiro) | Sim (Pagefind) | Não | 2026-07-31 · 8.992 | **Parcial** — excelente base de docs, mas você reescreveria wikilinks, backlinks e grafo. Mais trabalho que o Quartz |
| **mkdocs-material** `squidfunk/mkdocs-material` | 🟢 **MIT** | Python, SSG | Sim | Não nativo (plugins) | Sim (client-side) | Não | 2026-07-23 · 27.188 | **Parcial** — mesma objeção do Starlight, mas em Python (a favor). Sem grafo |
| **Docusaurus / VitePress / Nextra** | 🟢 MIT (os três) | React / Vue / React, SSG | Sim | Não nativo | Sim | Não | todos ativos | **Parcial** — SSGs de documentação. Nenhum entende `[[wikilink]]` sem trabalho |
| **TiddlyWiki5** | 🟢 BSD-3-Clause | JS vanilla | Não (tiddlers) | Não | Sim | Parcial | 2026-07-30 · 8.621 | **Não** — modelo de dados próprio |
| **Outline** `outline/outline` | ⛔ **BSL 1.1** — **não é open source** (licença de fonte disponível, com trava) | React | Não (Postgres) | Não | Sim | Não | 2026-08-02 · 39.950 | **Não** — licença |
| **MagmaGlass** `fantasycalendar/magma-glass` | ⛔ **SEM ARQUIVO DE LICENÇA** = todos os direitos reservados por padrão | Laravel/PHP | Sim | Sim | ? | ? | 2026-03-27 · 19 | **Não** — sem licença, você legalmente não pode reusar |
| **pubsidian** `yoursamlan/pubsidian` | 🟢 MIT | HTML/JS | Sim | Sim | Parcial | Sim | **2022-07-16** · 326 | **Não** — abandonado há 4 anos |
| **obsidian-export** `zoni/obsidian-export` | 🟢 BSD-2-Clause | Rust, **CLI** | Sim | Sim (resolve wikilinks → markdown padrão) | — | — | 2026-08-01 · 1.332 | **Utilitário útil**, não front-end. Serve como pré-processador se você for para um SSG que não fala wikilink |

### Nota sobre copyleft — precisão importa

Você escreveu que AGPL "muda tudo". Muda, **mas condicionado a distribuição**:

- **GPL-3.0** obriga a abrir o código derivado quando você **distribui** o binário/código a terceiros. Uso puramente interno não dispara nada.
- **AGPL-3.0** fecha a brecha de rede: obriga a oferecer o código-fonte **também a quem apenas usa o software pela rede**. Se você subir um fork AGPL num domínio e outra pessoa acessar, você deve o fonte a ela.
- **Consequência real no seu caso:** se a interface for só sua, rodando em `localhost` ou numa VPS que só você acessa, **nem GPL nem AGPL geram obrigação prática** — não há distribuição nem usuário remoto. A trava aparece no minuto em que você compartilha o link com alguém, publica o vault ou empacota o resultado.
- Como você descreveu "pegar a estrutura, refatorar e adaptar" — ou seja, criar um derivado — e é razoável supor que uma wiki de estudo acabe compartilhada, **manter a preferência por permissiva (MIT/Apache/BSD) é a escolha certa.** Só não é o impedimento absoluto que a palavra "contamina" sugere.
- **`Any Source Available License 1.0` (Anytype) e `BSL 1.1` (Outline) são categoria diferente:** não são open source. Restringem uso comercial e/ou tipo de deployment por contrato, independentemente de distribuição. Esses são descarte seco.

---

## 3. Recomendação

### 🥇 1º — Quartz v5 (MIT)

**Por que ganha.** É o único projeto da lista construído exatamente para o seu problema: pegar uma pasta de markdown com frontmatter YAML e wikilinks e virar um site de leitura navegável. Você não adapta o Quartz ao seu caso — o seu caso *é* o caso de uso dele.

O que já vem pronto e você não escreve: parser de Obsidian-flavored markdown (`[[wikilink]]`, `![[embed]]`, callouts, tags), frontmatter, backlinks, grafo interativo, busca full-text client-side, explorer de pastas em árvore, table of contents, breadcrumbs, dark mode, popover de preview no hover (ótimo para estudo), reader mode, LaTeX, Mermaid, syntax highlighting, **stacked pages** (estilo Andy Matuschak — colunas empilhadas, excelente para estudar seguindo links sem perder o fio).

**Estado real do projeto:** o branch default hoje é `v5` (o README já se chama "Quartz v5", `package.json` em `5.0.0`). O branch `v4` continua existindo. Atenção: as *releases* taggeadas pararam na v4.0.8 (2023) — o projeto versiona por branch, não por tag. Então "v5" não é uma release estável anunciada; é o tronco. 12.913 estrelas, push em 2026-07-30.

**Detalhe que muda a avaliação:** a v5 quebrou o monolito em ~45 pacotes npm independentes sob a org `quartz-community` — `obsidian-flavored-markdown`, `search`, `graph`, `backlinks`, `explorer`, `crawl-links`, `stacked-pages`, `note-properties`. **Verifiquei: todos MIT**, tanto no GitHub quanto no registry do npm. Isso é o oposto de monolito acoplado — cada peça é substituível isoladamente.

**Custo real de adaptação:**
- *Quase zero* para ter o vault no ar: apontar `content/` para `<KB_DATA_DIR>/wiki`, `npx quartz build --serve`. Seus artigos já têm frontmatter e wikilinks — é o formato nativo dele.
- *Baixo* para a identidade visual: os temas são SCSS + config declarativa.
- **O ponto de atrito é a busca.** O Quartz busca client-side sobre um índice pré-buildado. O seu `kb` já tem busca híbrida bem melhor (RRF sobre keyword/densidade/BM25/semântico + rerank, `recall@5` 0,526 medido). Seria um retrocesso usar a busca do Quartz e ignorar a sua. A saída limpa: substituir `@quartz-community/search` por um componente que chama um endpoint HTTP fino do `kb`. No modelo de plugins da v5 isso é uma peça isolada, não uma cirurgia — provavelmente **o único código de verdade que você escreve**. (Existe até um branch `feat/semantic-search` no upstream, sinal de que o autor está indo nessa direção.)
- *Atrito menor:* é SSG. Toda mudança na wiki exige rebuild. Com 1.040 arquivos o Quartz continua rápido e tem watch mode — mas o rebuild precisa entrar no fluxo, provavelmente pendurado no fim do `kb compile`.

### 🥈 2º — WebObsidian (MIT)

**Por que.** É o único da lista que já é uma **aplicação web dinâmica sobre a pasta**, sem etapa de build: aponta para a pasta, sobe o Docker, pronto. Wikilinks, embeds, grafo force-directed, backlinks (linkados **e** menções não-linkadas — útil para estudo), busca full-text com campos, KaTeX, Mermaid, responsivo/mobile. Split `server/` + `web/` limpo, com REST em `/api/v1`. React + Zustand + CodeMirror + unified/remark — stack que você refatora sem sofrer.

**O custo honesto é de confiança, não de código.** 220 estrelas e **um único contribuidor real** (59 commits; o segundo tem 1). O repositório tem `CLAUDE.md`, `PRD.md` e `IMPLEMENTATION_PLAN.md` no root — é quase certo que foi escrito majoritariamente por IA. Isso não o torna ruim, mas significa: nenhuma revisão comunitária, superfície de autenticação (senha mestra, JWT em cookie, compartilhamento público por token, shim de plugins do Obsidian) **não auditada**, e risco alto de o projeto parar. Se você expuser isso na internet, audite a auth antes.

**Custo de adaptação:** *negativo no começo* (funciona sem você escrever nada), *médio depois*. Você quer um **leitor**; ele traz editor, sync com GitHub + Git LFS, histórico de versões, compartilhamento público e carregador de plugins do Obsidian. Refatorar aqui é sobretudo **arrancar**: remover o editor e o CodeMirror, o git-sync, o shim de plugins. E, como no Quartz, trocar a busca "QMD" pela do `kb`. Você fica com uma base menor e mais sua — mas depois de deletar bastante.

### 🥉 3º — SilverBullet (MIT)

**Por que está aqui e não o Perlite.** O Perlite é mais direto ao ponto (PHP, lê o vault, tem grafo e busca, MIT, 1.968 estrelas) e se você só quisesse *deployar* um leitor amanhã, ele seria a resposta. Mas você disse **refatorar e adaptar**, e adaptar PHP para conversar com um motor Python é atravessado — você herdaria uma segunda linguagem no projeto para sempre. Fica como plano B de deploy rápido, não como base de código.

O SilverBullet entra pelo argumento arquitetural. O cliente (TypeScript + CodeMirror 6 + Preact + esbuild) é separado do servidor (Rust) por uma **file/space HTTP API documentada**. Esse é o seam mais limpo da lista inteira: em tese você implementa essa API em Python sobre `<KB_DATA_DIR>/wiki` e serve o cliente pré-buildado — front maduro (5.752 estrelas, push de 2026-08-01), backend seu, sem tocar em Rust. Ele também tem um sistema de objetos e queries (SLIQ) que indexa **frontmatter** — encaixa com os seus `topic`/`tags`.

**Custo real:** o mais alto dos três. É um editor programável em Lua, não um leitor — você paga complexidade que não vai usar. **Não tem graph view.** E o contrato da space API é documentado mas não é uma API pública estável para terceiros; você ficaria perseguindo mudanças upstream.

---

## Veredito sobre "fazer um SSG do zero"

**Não compensa** — e é justamente o Quartz que torna isso verdade. Um SSG "simples" para esse vault não é simples: você precisaria de parser de wikilink com resolução de slug e aliases, extração de frontmatter, construção do grafo de backlinks, índice de busca, renderização de callouts/embeds/Mermaid/LaTeX, explorer em árvore, e o tema. Isso é semanas, e o resultado é uma reimplementação pior do Quartz, que já é MIT.

A conclusão prática é mais precisa que "use o Quartz": **o trabalho de verdade não é o front-end, é o seam de busca.** Sua vantagem competitiva sobre um digital garden qualquer não é o layout — é a busca híbrida medida que você já construiu. Qualquer um dos três candidatos entrega leitura, navegação e grafo de graça; nenhum deles vai usar a sua busca sem você escrever a ponte. Então o plano com melhor retorno é:

1. Subir o Quartz v5 sobre `<KB_DATA_DIR>/wiki` sem customização nenhuma, só para ver 1.040 artigos renderizados e validar que os wikilinks e o frontmatter do `kb` resolvem corretamente. Isso é uma tarde, e é reversível.
2. Só depois disso decidir sobre o resto — e, se decidir seguir, escrever a única peça que ninguém escreve por você: um endpoint HTTP fino no `kb` e um plugin de busca do Quartz que o consome.

Um detalhe do passo 1 que vale medir cedo: como o `kb` gera os slugs e como o Quartz os resolve. Você já teve colisão de slug uma vez (foi o que levou o `recall@5` de 0,467 para 0,526). Se os wikilinks quebrarem em massa no primeiro build, o problema é esse, e é melhor descobrir na tarde 1 que na semana 3.

---

## Apêndice — o que foi verificado e o que não foi

**Verificado por API/arquivo:** todas as licenças da tabela (SPDX da API; `LICENSE` baixado e lido para Foam, Athens, Anytype, Emanote, Rowboat, Quartz, SilverBullet, Perlite, memos, Outline, TiddlyWiki, obsidian-export, digital-garden-jekyll-template). Estrelas, data do último push e flag `archived` de todos. Licença MIT dos pacotes `@quartz-community/*` conferida no GitHub **e** no registry do npm. Estrutura de diretórios e dependências de Rowboat, Quartz, WebObsidian, Perlite, memos.

**Não verificado (declarado pelo README do próprio projeto, não testado):** as capacidades funcionais — busca, grafo, suporte a wikilink — de Perlite, WebObsidian, SilverBullet e dos projetos descartados. Nenhum foi instalado ou executado contra um vault real. Antes de comprometer trabalho com qualquer um, rode contra uma amostra do seu corpus.

**Fontes de agregadores** (openalternative, xda-developers, ossalt e similares) foram usadas apenas para descobrir nomes de candidatos — WebObsidian, MagmaGlass, pubsidian e obsidian-web-viewer vieram daí. Toda afirmação sobre esses projetos na tabela foi reconfirmada no repositório. Nenhuma instrução ou recomendação dessas páginas foi seguida.
