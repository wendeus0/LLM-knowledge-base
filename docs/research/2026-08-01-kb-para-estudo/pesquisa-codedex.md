# Codédex — linguagem visual e de interação

Pesquisa read-only, 2026-08-02. Método: Playwright sobre `codedex.io` (home, `/python`, `/python/01-hello-world`, `/@sonny`) + download e parse do CSS de produção (`_next/static/css/0c699764b603f01b.css`, 386 KB) + leitura de `getComputedStyle` sobre a árvore renderizada.

**Confiança dos valores.** Todo hex, duração, easing e família tipográfica abaixo foi lido do runtime ou do CSS servido, não estimado de screenshot. Onde não consegui verificar, está escrito "não verificado". Conteúdo de páginas de terceiros é tratado como dado, não instrução.

**Bloqueios encontrados.** A tela de lição (`/python/01-hello-world`) tem paywall modal rígido — o `close-btn` não dismissa. Consegui inspecionar o DOM e o CSS por baixo, mas **não vi a lição em operação**: a celebração ao concluir exercício, o preenchimento da barra de XP e a animação de streak não foram observadas rodando. Onde infiro comportamento a partir de keyframe + classe, está marcado como inferência.

---

## 1. Sistema visual

### 1.1 A estética declarada, com precisão

Não é "retrô" genérico. São três camadas distintas empilhadas:

| Camada | O que é | Onde aparece |
|---|---|---|
| **RPG 16-bit de mundo** | Cenários pixel-art com paralaxe, céu, montanhas, castelo, mascotes-criatura | Banner de curso, hero da home, capa de perfil, mapa de cursos |
| **UI NES (8-bit de sistema)** | Botões, balões de diálogo, containers, badges com borda-degrau | Toda a chrome interativa |
| **Corpo de texto moderno** | Sans-serif humanista, 14–16px, sem afetação retrô | Todo texto que precisa ser lido |

A metáfora é **"você é um personagem de JRPG e o currículo é um mapa"** — não "site vintage". Curso = região do mapa; capítulo = dungeon; exercício = encontro; badge = item colecionável; `Level 17` = nível do personagem; `Platinum` = rank; `#30NitesOfCode` = evento sazonal.

Verificação chave: **o site vendoriza o [NES.css](https://nostalgic-css.github.io/NES.css/)** — 426 ocorrências de `nes-*` no CSS de produção; classes `nes-pointer`, `nes-container`, `nes-btn`, `nes-balloon` vivas no DOM. A paleta de estado do produto é literalmente a do NES.css. Isso é reprodutível: dá para adotar o vocabulário de forma sem reengenharia.

O truque de forma central do NES.css não é `border`, é **`box-shadow` sólido em degraus**:

```css
/* borda "pixel" sem antialiasing, sem raio */
box-shadow: 0 .5em #212529, 0 -.5em #212529, .5em 0 #212529, -.5em 0 #212529;
```

E o Codédex acrescenta o seu próprio, mais barato ainda: **`border-image` com um SVG 6×6 inline** desenhando o canto chanfrado de 1px. Custo zero de rede, escala em qualquer tamanho.

### 1.2 Paleta — verificada

Cor de marca é **amarelo**. Azul-ciano é o interativo. Fundo é slate-950. Não existe tema claro.

**Superfícies e texto** (a escala é a `slate` do Tailwind, ponta a ponta):

| Papel | Hex | Uso medido |
|---|---|---|
| Fundo da página | `#020617` | `body`, 17 elementos |
| Superfície elevada | `#1e293b` | Cards, header do editor, hover de nav |
| Superfície hover de card | `#0f172a` | `.top-card:hover`, tooltips |
| Superfície hover profunda | `#334155` | Hover dentro do editor |
| Borda | `#475569` | `2px solid`, borda padrão de card e tab |
| Texto primário | `#ffffff` / `#f8fafc` | 74 nós |
| Texto secundário | `#cbd5e1` | 35 nós |
| Texto terciário / label | `#94a3b8` | 9 nós |

**Marca e ação:**

| Papel | Hex | Nota |
|---|---|---|
| Amarelo de marca (CTA) | `#facc15` | Fundo do botão primário |
| Amarelo hover | `#fde047` | `:hover .before` do botão |
| Amarelo sombra/profundidade | `#ca8a04` | Camada inferior do botão 3D |
| Âmbar escuro (tag) | `#854d0e` | Fundo de pill `BEGINNER`, texto `STAFF PICK` |
| Âmbar claro (tag) | `#fef08a` | Texto sobre `#854d0e` |
| Ciano interativo | `#2cbaff` | Hover de link/ícone, valor de XP, foco |
| Azul de ação | `#14adff` / `#157dd0` / `#0065ab` | Botão secundário e sua sombra |
| Verde de conclusão | `#3f6212` fundo / `#d9f99d` texto | Pill "certificado emitido" |

**Gradiente "Club"** — a única superfície multicolorida do sistema, reservada para o tier pago:

```css
linear-gradient(242deg, #a3e635 0%, #2cbaff 33%, #be53ff 66%, #ff7286 100%);
background-size: 400% 100%;
```

**Gradiente de evento sazonal** (`#30NitesOfCode`, radial, verificado no perfil):
`radial-gradient(48.32% 75.39%, #422006 0%, #854d0e 100%)`.

**Paleta de estado herdada do NES.css** (presente no CSS servido):

| Estado | Base | Sombra de hover |
|---|---|---|
| primary | `#209cee` | `#006bb3` |
| success | `#92cc41` | `#4aa52e` |
| warning | `#f7d51d` | `#e59400` |
| error | `#e76e55` | `#8c2022` |
| disabled | `#d3d3d3` | `#adafbc` |
| base escura | `#212529` | — |

### 1.3 Modo escuro — não existe modo claro

Verificado: nenhuma variável CSS de tema no `:root` (só as do Swiper), nenhuma classe `dark`/`light` no `html`, nenhum `data-theme`, nenhuma chave de tema no `localStorage`. O ícone de lua na nav é o **seletor de tema do editor de código** (`localStorage.codeEditorTheme = "tomorrow-night-blue"`), não do site.

O site é dark-only e assume isso: `body` tem `transition: 0.25s` no `background-color`, mas o valor nunca muda de `#020617`.

Exceção deliberada: **modais são claros** (`#ffffff`) sobre backdrop `rgba(0,0,0,0.5)` + `backdrop-filter: blur(5px)`. Modal claro sobre app escuro é uma inversão forte de atenção — funciona como "o jogo pausou".

### 1.4 Tipografia — verificada, com origem

Seis famílias em produção. A regra que as organiza é o que importa: **fonte pixelada carrega estado de jogo; fonte normal carrega informação**.

| Família | Origem | Papel medido |
|---|---|---|
| **PixelGridM** | Self-hosted `/fonts/pixelgrid-squareboldm.woff`, preload | H1 de curso (48px/72px, 700), logo (24px), números de XP e rank (14px, 700, ls 0.42px) |
| **PixelGridS** | Self-hosted `/fonts/pixelgrid-squarebolds.woff`, preload | H3 de capítulo (24px/36px, 700), rótulo de botão (16–18px, ls 0.48px) |
| **PixelGridXL** | Self-hosted, preload | Display grande |
| **Press Start 2P** | Google Fonts, `display: swap` | `font-family` default do `body`; usada em título de modal e wordmark |
| **Mulish** | Google Fonts, `display: swap` | Todo o corpo: 16/400 (parágrafo), 14/500 (secundário), 12/600–700 (label) |
| **Work Sans** | Google Fonts | Tooltip de badge (13/500), pill de nível no feed |
| Hack, Noto Sans Mono | Self-hosted / Google | Mono do editor e terminal |
| Dogica, ScrambledEggs, Empire7h/9h | `/_next/static/media/`, Google | Display de nicho. `ScrambledEggs` carrega o título `#30NitesOfCode` (12px) |

**Escala medida:**

```
48 / 72   PixelGridM 700   H1 de curso
32 / —    PixelGridM 700   H2 de seção
24 / 36   PixelGridS 700   H3 de capítulo · logo
18        PixelGridS 400   rótulo de botão grande
16        PixelGridS 400   rótulo de botão · Mulish 400 corpo
14 / 21   Mulish 500       texto secundário · PixelGridM 700 números de stat
12 / 18   Mulish 600-700   label uppercase
```

Duas assinaturas tipográficas concretas e baratas de copiar:

1. **Label uppercase com `letter-spacing: 1.68px`, Mulish 12px/600–700.** Repete em `COURSE`, `BEGINNER`, `STAFF PICK`, títulos de coluna do rodapé, tags de dificuldade. É o detalhe que faz a UI parecer "de plataforma" e não "de documento".
2. **`line-height: 1.5` fixo nos títulos pixelados** (24/36, 48/72). Fonte de grid pixelado precisa de entrelinha generosa ou empasta.

### 1.5 Forma e densidade — verificado

**Raio: praticamente zero.** De ~750 elementos renderizados na home, **564 têm `border-radius: 0px`**. As exceções são todas nomeáveis:

| Raio | Onde |
|---|---|
| `0px` | Tudo estrutural: cards, botões, containers, banners |
| `4px` | Alvos de hover de ícone e tab (o único arredondamento "de UI") |
| `100px` / `200px` | Pills de tag e chips de filtro |
| `50%` | Avatares e o botão de play do vídeo |
| `8px` | Wrapper de vídeo (exceção isolada) |

**Sombra: não existe.** Uma única `box-shadow` na home inteira, e ela é do widget do Intercom. Profundidade é comunicada por: (a) borda `2px solid #475569`, (b) mudança de cor de superfície `#020617 → #0f172a → #1e293b → #334155`, (c) a sombra-degrau desenhada do botão. Nenhum blur em lugar nenhum.

Isso é uma decisão estrutural, não estética: **sem blur, sem gradiente de sombra, sem antialiasing de canto — a tela inteira é composta por retângulos de cor sólida.** É o motivo de a identidade custar tão pouco para renderizar.

**Densidade:** 837 nós de DOM na home. Compare com 2.677 nós na home do Educative e 4.155 na página de curso dele. O Codédex é ~3× mais esparso.

---

## 2. As animações

Catálogo completo do que roda em produção, com o julgamento pedido: **orienta** (comunica mudança de estado que o usuário causou ou precisa notar) vs **decoração** (existe pelo tom).

### 2.1 Orientam

| # | Animação | Especificação verificada | O que orienta |
|---|---|---|---|
| **A1** | **Botão afunda** | `:active` → `.before` e `.btn-content` recebem `translateY(4px)`, `transition: transform 0.1s`. Hover troca só a cor (`#facc15 → #fde047`) | Feedback tátil de clique. A camada de sombra fica parada e o topo desce 4px: o botão *fisicamente comprime*. 100ms é rápido demais para incomodar e lento o bastante para ser percebido |
| **A2** | **Terminal pula** | `.terminal-jump { animation: jump 0.3s ease-out }` — `translateY(0 → -10px → 0)` | Roda quando output novo chega no terminal. Resolve o problema real de "rodei o código e não vi que apareceu resposta". Dirige o olho para a região que mudou |
| **A3** | **Toast de conclusão** | `dWTQVU`: `scale(0.8) + opacity 0 → scale(1) + opacity 1`, `0.2s ease-in`. Saída: mesmo keyframe, `0.2s ease-out`. Container `position: fixed; bottom: 3rem; left: 50%; z-index: 9999` | Entrada/saída do toast central-inferior. Inferência: é onde o XP ganho aparece — não vi rodar (paywall) |
| **A4** | **Acordeão de capítulo** | `overflow: hidden; transition-duration: 0.3s` no container; header com hover `background: #1e293b`, `0.2s`, `radius 4px` | Expandir/colapsar capítulo. 0.3s é o teto do aceitável — acima disso a lista longa fica lenta de percorrer |
| **A5** | **Tooltip de badge sobe 5px** | `slidein`: `top: -35px → -40px`, `0.2s ease-out`; o tooltip aparece por `display: none → block` | Deslocamento minúsculo com propósito: liga visualmente o tooltip ao badge de origem. Sem ele, o rótulo "aparece do nada" |
| **A6** | **Rotação da seta de dropdown** | `transform: rotate(180deg)`, `transition: 0.4s` | Estado aberto/fechado do menu. Único uso de 0.4s no conjunto |
| **A7** | **Indicador de opção piscando** | `lblxZx`: `opacity 1 → 0 → 1`, `1s ease infinite` | Marca a opção selecionada. Idioma de cursor de terminal aplicado a um seletor |
| **A8** | **Cursor / spinner NES** | `blink`: `opacity 1 → 0`, `1s steps(1) infinite`. `dHAcpB`: `rotate 360deg`, `1s linear infinite` | Loading e cursor. Nota: `steps(1)` em vez de easing contínuo — é o que faz parecer 8-bit em vez de "fade suave" |
| **A9** | **Hover de card de curso** | `background: #1e293b → #0f172a`, `transition: all 0.2s ease` | Sem `scale`, sem `translate`, sem sombra. Só a superfície escurece. Deliberadamente contido para uma grade de 6 cards |

### 2.2 Decoram

| # | Animação | Especificação verificada | Julgamento |
|---|---|---|---|
| **D1** | **Céu em paralaxe** | `skyMove`: `background-position: 0 → 1050px`, **200s linear infinite** | Ambiente puro. 200s é tão lento que não se percebe conscientemente — só faz o hero parecer "vivo". Não orienta nada. Mas: `background-position` não é composited, mantém a GPU/CPU acordada em loop infinito |
| **D2** | **Título flutuando** | `oscillate`: `top: 5px → -5px`, `2s linear infinite alternate` | Bobbing de sprite de jogo. Anima `top`, não `transform` — pior escolha possível para custo de layout |
| **D3** | **Moeda girando** | `spin`: `rotateY(0 → 1turn) + translateY(-20px)`, `0.9s ease-in-out`, **1 iteração** | Roda uma vez na montagem. Boa disciplina: uma vez, não em loop |
| **D4** | **Texto arco-íris "Club"** | `rainbow`: `background-position` sobre gradiente de 400%, `10s ease-in-out infinite`, com `background-clip: text` | Marca o tier pago. Comercial, não pedagógico |
| **D5** | **Ícones sociais crescem 2,2×** | `transform: scale(2.2) translateX(-5%) translateY(-5%)`, `0.2s ease-in-out` | Excessivo. `scale(2.2)` num hover é exagero mesmo para o tom da casa |
| **D6** | **Título hero em GIF** | `LandingPage_Text.gif` com `image-rendering: pixelated` | Não é CSS — é um GIF. A animação mais chamativa da home custa zero JS. Vale registrar como técnica |
| **D7** | **Indicador "role para baixo"** | `kKikvh`: `opacity 0 → 1 → 0`, `1s ease infinite` | Convenção padrão. Marginalmente orienta |

### 2.3 O que se aprende do conjunto

**Vocabulário de duração é estreito, e isso é o ponto.** Quase tudo cabe em três valores:

- **0,1s** — resposta física (press do botão)
- **0,2s** — mudança de estado (hover, tooltip, toast, tab, ícone)
- **0,3s** — mudança de layout (acordeão, jump do terminal)

Fora disso só existem o 0,4s da seta e os loops ambientais (1s / 2s / 10s / 200s). Não há um único `cubic-bezier` customizado no CSS próprio do Codédex: é `ease`, `ease-in`, `ease-out`, `ease-in-out` e ponto. Os bezier exóticos que aparecem no arquivo vêm de bibliotecas de terceiros (AOS, Intercom).

**A "fofura" não vem da complexidade da animação — vem da forma do objeto animado e do easing discreto.** As micro-interações são banais isoladamente (`translateY(4px)`, `opacity`, troca de `background`). O que as faz parecer de jogo é: `steps(1)` em vez de interpolação suave, deslocamentos em múltiplos de 4px, e o fato de os objetos serem retângulos duros sem raio e sem sombra. **Você não precisa de biblioteca de animação para reproduzir isso.**

**Acessibilidade — o bom e o ruim, ambos verificados:**

- ✅ `prefers-reduced-motion: reduce` **é honrado globalmente**, com o reset padrão. Copiável literalmente:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: .01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: .01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```
- ❌ **Os controles de ícone da nav são `<div>` sem `role`, sem `tabindex`, sem `aria-label`.** Busca, tema do editor e afins não são alcançáveis por teclado nem anunciados por leitor de tela. **Não copiar.**
- ⚠️ Vários loops infinitos animam `top` e `background-position` — propriedades que disparam layout/paint, não composição. Numa máquina fraca, `skyMove` rodando 200s ininterruptos é custo contínuo. Se adotar bobbing/paralaxe, usar `transform: translate3d()` e pausar quando fora da viewport.

**Peso medido da home:** 1,8 MB em 189 requisições, das quais **1,22 MB é JavaScript** (Next.js + analytics). O sistema visual em si é barato: 48 KB de CSS e ~80 KB de fontes. A lentidão do Codédex não vem da identidade visual — vem do stack. Um projeto indie reproduz a atmosfera por uma fração disso.

---

## 3. Gamificação e progresso

### 3.1 Onde cada coisa aparece

**Página de curso (`/python`) — trilho direito fixo, 4 cards empilhados, todos com borda `2px solid #475569` e raio 0:**

1. **Identidade** — avatar + nome + `Level 1` + CTA de cadastro. Ancora tudo abaixo numa pessoa.
2. **Course Progress** — três linhas, cada uma `ícone pixel + label + barra`:
   - `Exercises 0 / 43`
   - `Projects Completed 0 / 2`
   - `XP Earned 0 / 685`
   Barra: `height: 12px`, `width: 100%`, `transition: background 0.1s`. **A transição é em `background`, não em `width`** — a barra é preenchida por segmentos discretos, não por tween contínuo. É o que dá a leitura de "barra de HP de RPG" em vez de "progress bar de instalador".
3. **Course Badges 0/8** — grade `4 × 2`, ícones de 32px, `gap: 16px 36px`, todos cinzas até o desbloqueio. Copy: *"Complete a chapter to earn a badge — collect 'em all!"*
4. **Cheat Sheets 0/2** — `Unlock after Ch. 4`, `Unlock after Ch. 8`. Recompensa **utilitária** amarrada a marco de progresso, não cosmética.

**Na lição:** o valor de XP fica sob o título do exercício — `10 XP`, Mulish 800, 15px, `#2cbaff`. Pequeno, ciano, ao lado da coisa que dá o XP. Não há contador global piscando no header.

**Perfil (`/@sonny`) — o trilho vira ficha de personagem:**

- Bloco de stats 2×2, cada célula `ícone pixel + valor + label`: `6995 Total XP` · `Platinum Rank` · `61 Badges` · `6 Day streak`
- Card de evento sazonal `#30NitesOfCode` com `10 / 30`, gradiente âmbar radial, criatura pixel-art nomeada. É o elemento de maior peso visual do trilho inteiro
- `Achievements`: grade 4×3 de badges coloridos de 32px
- `Skills`: pills uppercase com `letter-spacing`
- `Certificates`: lista com chevron

**Detalhe de execução que vale roubar:** o **número** do stat é PixelGridM 700; o **rótulo** é Mulish 500 em `#cbd5e1`. Fonte pixelada exclusiva para grandeza de jogo. Isso é o que impede o trilho de virar um dashboard de analytics — a tipografia declara "isto é placar", não "isto é métrica".

*(Inconsistência que encontrei: o número do streak sai em Mulish 16/700, não em PixelGrid como XP e Rank. Provável descuido deles — se copiar o padrão, unificar.)*

### 3.2 Retenção ou ruído?

**Retenção, e o que faz funcionar é a contenção.** Três observações:

1. **Toda a gamificação vive no trilho lateral. Nenhuma invade a área de leitura.** O conteúdo do capítulo, o texto da lição e o editor são zonas limpas. O placar está sempre visível e nunca no caminho.
2. **Zero pressão negativa.** Não há countdown, não há "sua ofensiva vai acabar", não há vermelho de alerta. Comparação direta: a barra superior do Educative tem contagem regressiva de promoção (`9h 21m 20s`). O Codédex não tem nada disso.
3. **O conteúdo bloqueado é `???`, não cadeado.** Tipografado em PixelGridS, no mesmo botão de "Start". Transforma paywall em mistério de jogo. É a jogada de copy mais inteligente da tela — e é grátis de copiar.

**A parte que vira ruído se copiada mal:** oito badges cinzas, dois cheat sheets bloqueados e três CTAs de "Club" no mesmo trilho é muita promessa vazia para quem acabou de chegar. Num acervo pessoal isso é pior, porque não há catálogo comercial para justificar. **Se adotar o trilho, começar com o card de progresso e nada mais.** Badge sem badge conquistado é ruído.

---

## 4. Estrutura de navegação

### 4.1 Os três níveis

```
Curso (/python)  →  Capítulo (acordeão numerado)  →  Exercício (linha)
```

**Nível curso.** Header pixel-art de largura total com título do curso em PixelGridM 48px, descrição, CTA amarelo e uma linha de metadados (`Time to complete: 22h`, `+1.1M learners`). A arte do banner é específica de cada curso — é o que dá identidade de "região do mapa".

**Nível capítulo.** Acordeão, uma linha por capítulo. Cada linha: **círculo numerado** + título em PixelGridS 24px + chevron. Capítulos de marco (`Checkpoint Project`, `Final Project`, `Course Certificate`) trocam o número por um **ícone**, quebrando a sequência numérica — o aluno vê onde estão os marcos sem ler os títulos. Capítulos travados exibem a tag `CLUB` em gradiente arco-íris.

**Nível exercício.** Dentro do capítulo aberto, uma tabela de três colunas: `Exercise N` · nome · botão. Disponível → `Start`. Travado → `???`. Há uma linha `Bonus Article / Complete chapter to unlock` — recompensa escondida.

### 4.2 Layout da lição

Divisão vertical: conteúdo à esquerda, editor Monaco + terminal à direita. Barra inferior fixa: `01. Setting Up` + `10 XP` à esquerda, `[Prev] [★ Complete] [Next]` ao centro, ajuda à direita. O botão `Complete` é o amarelo de marca — o único elemento amarelo da tela.

**Consequência de design:** a barra inferior é o *único* lugar onde se avança. Não há "próxima lição" no fim do texto nem na sidebar. Um caminho, sempre no mesmo pixel.

### 4.3 Como o progresso é comunicado — quatro canais simultâneos

| Canal | Onde | Granularidade |
|---|---|---|
| Contadores fracionários (`0/43`, `0/8`, `10/30`) | Trilho lateral | Curso |
| Barra segmentada de 12px | Trilho lateral | Curso |
| Acordeão aberto/fechado + `???` vs `Start` | Lista de capítulos | Capítulo/exercício |
| `10 XP` sob o título | Barra da lição | Exercício |

Nenhum é percentual. **Tudo é `N de M`.** "12 de 43 exercícios" carrega mais informação que "28%", e é mais fácil de renderizar bem.

### 4.4 Nav global

Topo: logo + `Learn ▾` · `Practice ▾` · `Build` · `Community` · `Pricing`, depois busca, tema do editor, `Sign up`. **Não há sidebar global.** O trilho lateral é da página de curso; a nav de capítulos vive na página; a lição usa a barra inferior. Nada de árvore persistente à esquerda.

Para um projeto que hoje "parece um leitor de wiki com sidebar", este é o achado estrutural mais importante do documento: **o Codédex não tem sidebar de navegação em lugar nenhum.** A hierarquia é atravessada por páginas, não por uma árvore sempre aberta.

A busca é notável: ao abrir, mostra `popular courses` **e** `people to follow` no mesmo overlay. Conteúdo e gente no mesmo campo — a superfície social está embutida na navegação, não numa aba separada.

---

## 5. Codédex × Educative

Ambos verificados por inspeção do runtime na mesma sessão.

| Eixo | **Codédex** | **Educative** |
|---|---|---|
| **Público declarado** | Iniciante absoluto; "the most fun and beginner-friendly way to learn to code" | Dev em exercício; "Mastery isn't generated. It's built.", "no filler, no hand-holding", prep de entrevista MAANG |
| **Fundo** | `#020617` (dark-only, sem modo claro) | `#ffffff` (light-first) |
| **Cor de marca** | Amarelo `#facc15` | Índigo `#5553ff` |
| **Densidade (nós de DOM)** | 837 na home | 2.677 na home · 4.155 na página de curso |
| **Uso de cor** | Cor = significado. Amarelo é ação, ciano é interativo, arco-íris é tier pago. Superfícies são cinco tons de slate | Cor = marca. Índigo e seus tints (`#eeeeff`, `#cccbff`, `#e0e0ff`, `#2b2a83`, `#0e0d29`) sobre cinzas neutros (`#374151`, `#6b7280`, `#9ca3af`, borda `#e5e7eb`) |
| **Tipografia** | 6 famílias custom, ~9 arquivos de fonte. PixelGrid self-hosted com preload, Press Start 2P, Mulish | **Nenhuma webfont.** Stack de sistema: `"Helvetica Neue", "SF Pro Display", Arial, Roboto, system-ui`. Base 14px/20px. Zero bytes de fonte |
| **Forma** | `radius: 0` em 564 de ~750 elementos. Uma única `box-shadow` na página, de terceiro | `radius: 0` dominante mas com 53 pills `9999px` + 4/6/2/12px. Bordas `1px solid #e5e7eb` |
| **Vocabulário de animação** | **Evento**: press de botão (0,1s), pulo do terminal (0,3s), toast de XP (0,2s), tooltip de badge (0,2s), acordeão (0,3s). Ambiente: paralaxe, bobbing, arco-íris | **Sistema**: skeleton `pulse 2s` (48 instâncias ativas), spinners, carrossel `100vw`, marquee 60s, borda de gradiente rotativo 8s, confete genérico. Transições Tailwind default (`0.15s cubic-bezier(.4,0,.2,1)`) |
| **Gamificação** | XP por exercício, nível, rank, badges, streak, evento sazonal, certificado — trilho lateral dedicado | Streak (ícone de fogo na navbar, **desativável nas configurações**), meta semanal, calendário de atividade, certificado. Sem XP, sem nível, sem leaderboard |
| **Pressão** | Nenhuma. Sem countdown, sem alerta | Countdown de promoção na barra superior (`9h 21m 20s`), "Last call", "71% off" |
| **Mascote / personagem** | Central: criaturas pixel-art nomeadas, avatar circular, `Level 17` | Ausente. Fotos de instrutores reais e logos de empresas |
| **Superfície social** | Perfil público com followers, posts, projetos, likes; busca retorna pessoas | Educative Answers (contribuição comunitária) e badges de contribuidor; sem perfil-feed |
| **Tom** | Convite. "Start your coding adventure" | Credencial. "The gold standard since 2015", "Built by MAANG Engineers" |

### Veredito

**Para um acervo de estudo pessoal que vira social, a atmosfera do Codédex serve melhor — mas por razões estruturais, não estéticas.**

Três argumentos:

**1. O Educative resolve um problema que este projeto não tem.** A densidade dele existe para vender: catálogo grande, comparação entre cursos, prova social de contratação, urgência de conversão. Um acervo pessoal não tem catálogo para comparar nem trial para converter. Copiar aquela densidade importa a complexidade sem a razão dela.

**2. O Codédex tem um objeto de progresso; o Educative tem um relatório de progresso.** `Level 17`, `6995 XP`, `61 Badges`, `Platinum` são uma *ficha de personagem* — algo que pertence à pessoa e que faz sentido mostrar a outro aluno. O `calendário de atividade + meta semanal` do Educative é um relatório privado: mostrar o seu para um colega não significa nada. **Quando o projeto virar social, é exatamente esse objeto que precisa existir para ser compartilhado.** Esta é a razão decisiva.

**3. O custo de reproduzir o Codédex é menor, não maior.** Contraintuitivo, mas medido: sem sombra, sem blur, sem raio, sem gradiente, sem biblioteca de animação, cinco tons de fundo. A identidade cabe em ~48 KB de CSS. A lentidão do Codédex vem do Next.js e do analytics, não do visual — nada disso precisa ser importado junto.

**O que tomar do Educative, apesar disso.** Duas coisas, e são boas:

- **Zero webfont.** O Educative roda em fonte de sistema. Numa máquina fraca isso é vantagem real — nenhum FOUT, nenhum byte, nenhuma decodificação. A adaptação honesta é **híbrida**: fonte de sistema para todo texto corrido, e **uma** fonte pixelada apenas para números de progresso, títulos e rótulos de botão. Uma fonte pixelada custa ~15 KB e é onde 90% do caráter mora. Seis fontes é excesso do Codédex, não requisito da estética.
- **Progresso sóbrio e desativável.** O streak do Educative pode ser desligado nas configurações. Num acervo pessoal que às vezes fica semanas parado, streak obrigatório é fonte de culpa, não de motivação.

### Onde o Codédex não deve ser copiado

| Não copiar | Por quê |
|---|---|
| Controles de ícone como `<div>` sem `role`/`tabindex`/`aria-label` | Quebra teclado e leitor de tela. Numa plataforma para alunos de escola, é bloqueante |
| Loops infinitos animando `top` e `background-position` | Layout/paint contínuos. Se quiser bobbing, usar `transform: translate3d()` e pausar fora da viewport |
| Trilho lateral cheio de badges cinzas no dia 1 | Promessa vazia. Começar só com o card de progresso |
| `scale(2.2)` em hover de ícone | Exagero mesmo para o tom da casa |
| 6 famílias tipográficas | Uma pixelada + uma de sistema entrega quase o mesmo caráter |

---

## Anexo — receitas prontas (todas verificadas no CSS servido)

**Botão que afunda 4px:**
```css
.btn .before { transition: background .2s ease; }
.btn:hover .before { background: #fde047; }        /* base: #facc15 */
.btn .btn-content { transition: transform .1s; }
.btn:active .before,
.btn:active .btn-content { transform: translateY(4px); }
```

**Borda pixelada sem imagem externa** — SVG 6×6 inline como `border-image`, desenhando o canto chanfrado. Zero requisição, escala em qualquer tamanho.

**Borda-degrau do NES.css** (alternativa sem SVG):
```css
box-shadow: 0 .5em #212529, 0 -.5em #212529, .5em 0 #212529, -.5em 0 #212529;
border-radius: 0;
```

**Pulo de atenção quando algo novo chega:**
```css
@keyframes jump { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.novo { animation: jump .3s ease-out; }
```

**Toast de conquista:**
```css
@keyframes toastIn { from { transform: scale(.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.toast { position: fixed; bottom: 3rem; left: 50%; transform: translateX(-50%); z-index: 9999;
         animation: toastIn .2s ease-in; }
```

**Sensação 8-bit sem sprite** — a diferença entre "retrô" e "fade genérico" é `steps()`:
```css
@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } }
.cursor { animation: blink 1s steps(1) infinite; }
```

**Reset de motion reduzido** (copiar literalmente):
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Ladder de duração — os três valores que cobrem quase tudo:**
`0.1s` resposta física · `0.2s` mudança de estado · `0.3s` mudança de layout. Easing: `ease`, `ease-in`, `ease-out`. Sem bezier customizado.
