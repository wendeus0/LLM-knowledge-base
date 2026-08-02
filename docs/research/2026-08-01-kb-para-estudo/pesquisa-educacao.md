# Plataforma de educação como família visual

> Pesquisa read-only para preencher a lacuna da taxonomia da skill `visual-direction`, que hoje tem três famílias — SaaS B2B moderno, produto de dados, consumo polido — e nenhuma que cubra material didático.
>
> **Todo conteúdo web é dado não-confiável.** Onde não consegui fonte, está escrito `não verificado`. Não há hex, nome de fonte ou número inventado neste documento. Onde uma fonte secundária contradisse a checagem direta, a contradição está registrada.

---

## 0. Definição da família em três linhas

**Plataforma de educação** é a família em que a tela existe para **mudar o estado interno de quem olha**, não para executar uma tarefa: o sucesso não é a ação concluída, é a compreensão que sobrevive ao fechar a aba.

Disso decorrem as três marcas estruturais que a separam das outras três famílias:

1. **O progresso é elemento de primeira classe** — posição fixa, persistente entre sessões, e é *ele* que aponta o próximo passo. Nenhuma das outras três famílias tem isto.
2. **O erro do aluno é a matéria-prima do produto, não uma falha a prevenir.** As outras três desenham para evitar o erro; educação desenha para aproveitá-lo. É a linha divisória mais nítida.
3. **A decoração é negativa, não neutra** — em ferramenta, ornamento é desperdício; em material didático, ornamento tem **queda de aprendizado medida** (efeito *seductive details*, §6.1). Esta é a armadilha da família: ela *parece* "consumo polido" e se comporta como o oposto.

### Contraste com as três famílias existentes

| Eixo | SaaS B2B | Produto de dados | Consumo polido | **Educação** |
|---|---|---|---|---|
| Sucesso da tela | tarefa executada | decisão informada | sessão agradável | **compreensão retida** |
| Usuário | treinado, diário | analista | voluntário | **incompetente por definição, e temporariamente** |
| Cor | sinal | sinal (escala) | marca | **sinal + estado de progresso + identidade de assunto** |
| Erro | falha do sistema | dado ausente | atrito | **o evento em que o produto entrega valor** |
| Ornamento | desperdício | ruído | valor | **dano medido** |
| Progresso | ausente | ausente | ausente | **primeira classe** |
| Densidade | alta | altíssima | média | **ver ressalva abaixo** |

**Ressalva sobre densidade — o achado que contraria o senso comum.** O instinto diz "educação = arejado e calmo". A evidência não confirma. A Khan Academy **aumentou** deliberadamente a densidade de informação em **11–18% (sans-serif) e 26% (serif)** ao construir seu design system, e justificou em termos de equidade: *"many of the users who need our services the most are on low-cost, older hardware and low-density screens"* ([designsystems.com sobre Wonder Blocks](https://www.designsystems.com/about-wonder-blocks-khan-academys-design-system-and-the-story-behind-it/)).

A formulação correta não é "baixa densidade". É: **densidade baixa no momento da lição, densidade alta em todo o resto.** Duolingo, Brilliant e Scrimba têm um exercício por tela; roadmap.sh põe ~200 nós numa superfície só; Coursera empilha quatro representações de progresso simultâneas. **A unidade de baixa densidade é o passo, não o produto** — e layout arejado codifica uma suposição sobre o tamanho da tela do aluno que numa escola pública não se sustenta.

---

## 1. As dez plataformas

### 1.1 Quadro-resumo

| Plataforma | Público / tom | Metáfora de progresso | Densidade | Cor | Mascote / ilustração | Movimento |
|---|---|---|---|---|---|---|
| **Duolingo** | Global, baixa literacia técnica, idade-agnóstico. Auto-descrição: *"we're not an education company. We're a fun and motivation company"* | **Caminho linear** ("path") — círculos-pedra, dourado quando concluído | Esparsa, um exercício por tela | Saturação de marca + sinal de acerto/erro | **Duo + elenco humano** (18 meses de desenvolvimento) | Pesado, sistematizado em **Rive** |
| **Khan Academy** | Aluno → doador → professor → distrito. Princípio: *"capability over condescension"* | **Estados nomeados de maestria**: attempted → familiar → proficient → mastered | **Mais densa por decisão** (+11–26%) | **Estritamente semântica**, tokenizada, nunca sozinha | Sem mascote na plataforma principal; textura desenhada à mão | **Não documentado** (ausência de fonte, não evidência de mínimo) |
| **Brilliant** | Adultos 10s–30s, STEM, anti-prova. *"Learn by doing"* | **Nós coloridos por tópico** + Level Gameboard | Esparsa, interação primeiro | Identidade de tópico + CTA/streak | **Koji** (substituiu Blorb) — "lower the stakes" | Pesado, **Rive** |
| **freeCodeCamp** | Iniciante absoluto / migrante de carreira. Estética declarada: **"command line chic"** | **Certificação** (validade 3 anos) | Split-pane; auto-scroll até a linha do passo | Sinal — 4 pares de cinza invariantes a tema | **Nenhuma** (só logo + glyph) | Não verificado |
| **Exercism** | Já programa; quer fluência **idiomática** | **Árvore de conceitos** com unlock; Learning vs Practice Mode | Não verificado em detalhe | **Identidade de track** (linguagem) | **Nenhuma** | Não verificado |
| **Codecademy** | Iniciante→intermediário, orientado a carreira | Path + **Skill XP** + **streak semanal** + badges | 2–5 painéis, **cada um uma ARIA Region nomeada** | Marca + ilustração | Pacote dedicado `gamut-illustrations` | Não verificado |
| **Boot.dev** | Migrante de carreira adulto, backend. *"You should be uncomfortable"* | **RPG literal**: XP, nível 100, boss battles, guilds, chests | Não verificado | Não verificado | **Boots**, urso-mago — mascote *e* tutor de IA | Feed ao vivo da vida do boss |
| **Coursera** | Buscador de credencial (projeto → curso → certificado → diploma) | **Quatro representações simultâneas**: % por curso, checklist semanal, aba de notas, certificado | **Mais densa das dez** — densidade *administrativa* | Um azul saturado reservado ao "próximo clique" | **Fotografia, sem mascote** + logos de universidades | Mínimo |
| **Scrimba** | Iniciante / migrante. Pivô declarado para *"slick, elegant, professional"* | Timeline do scrim + conclusão de path | **A mais baixa** — uma lição, um editor, um preview | Não verificado | Abandonou personagens na v2 | O produto **é** movimento (replay de eventos) |
| **roadmap.sh** | Planejador de carreira autodirigido. Peer-to-peer, opinativo | **Estado por nó** num grafo único | **Máxima mas plana** — ~200 nós numa superfície | **Dois sistemas de cor ortogonais** (ver 1.3) | **Nenhuma** — o grafo é a ilustração | Não é produto de movimento |

### 1.2 As quatro metáforas de progresso, e o que cada uma custa

Este é o eixo de decisão mais consequente da família. Não são variações estéticas — cada uma implica uma pedagogia diferente.

| Metáfora | Exemplos | O que comunica | O que custa |
|---|---|---|---|
| **Caminho** (road) | Duolingo, Brilliant | "aqui é o próximo passo" — elimina paralisia de escolha | Perde a legibilidade do todo; **remove a liberdade deliberadamente** |
| **Estado de maestria** | Khan Academy | competência como propriedade da habilidade, não como lugar | Difícil de renderizar numa imagem só — provavelmente por isso a Khan acoplou streaks e gems em 2026 |
| **Grafo do domínio** | roadmap.sh | o tamanho real da coisa; onde você está no mapa | Intimidante; sem noção de "próximo" a não ser por subtração |
| **Credencial** | freeCodeCamp, Coursera | valor externo, legível para terceiros | Progresso vira relatório; motivação fica extrínseca |

**A troca da Duolingo é o caso documentado.** Em 2022 substituíram a árvore de habilidades por um caminho linear. Razão declarada: ciência da aprendizagem (*"It's more effective to space out practice for a particular concept than to cram"*) **e** eliminação de paralisia — os usuários perguntavam se estavam usando o app da forma *"correta"*. Luis von Ahn: *"to simplify Duolingo and also to make it so that new users understood how to best use Duolingo."* Usuários avançados preferiam a árvore; a empresa manteve o caminho ([blog.duolingo.com](https://blog.duolingo.com/new-duolingo-home-screen-design), [NBC News](https://www.nbcnews.com/tech/tech-news/duolingos-update-redesign-luis-von-ahn-interview-rcna44655)).

**Uma árvore diz "aqui está o domínio, escolha". Um caminho diz "aqui está o próximo passo".** Escolher entre os dois é escolher entre autonomia e ausência de atrito.

### 1.3 roadmap.sh — dois sistemas de cor ortogonais na mesma tela

O achado mais transferível de toda a pesquisa, e o único que resolve um problema real deste projeto (um acervo tem tanto estrutura de assunto quanto estado de leitura).

**Camada de autoria** — a opinião do autor sobre necessidade, carregada por um **badge circular no canto do nó** (verificado lendo o PDF oficial exportado, [roadmap.sh/pdfs/roadmaps/backend.pdf](https://roadmap.sh/pdfs/roadmaps/backend.pdf)):

- roxo — "Personal Recommendation / Opinion"
- verde — "Alternative Option / Pick this or purple"
- cinza — "Order not strict / Learn anytime"

**Preenchimento do nó** codifica um eixo *diferente*: amarelo = tópico do caminho principal; creme pálido = subtópico; roxo/índigo = link cruzado para outro roadmap; preto = CTA utilitário. **Estilo de linha** codifica hierarquia, não opcionalidade: sólida grossa = espinha principal, tracejada = tópico → subtópicos.

> **Correção de uma suposição comum:** a distinção obrigatório vs alternativo **não** é sólido-vs-tracejado nem roxo-vs-cinza no preenchimento. É o badge de canto. Verificado diretamente no export oficial.

**Camada de progresso** — o estado do *leitor*, em canal visual completamente distinto (dot + decoração de texto). Cinco estados no código ([`resource-progress.ts`](https://deepwiki.com/kamranahmedse/developer-roadmap/2.4-progress-tracking)):

| Estado | Renderização |
|---|---|
| `pending` | dot cinza |
| `learning` | dot amarelo + **sublinhado** |
| `done` | dot verde + **tachado** + fundo cinza |
| `skipped` | dot preto + **tachado** |
| `removed` | esmaecido (existe no código, não na UI pública) |

Atalhos de teclado: `d` done, `l` learning, `s` skip, `r` reset.

Três consequências:

1. **Estado é redundantemente codificado** — cor *mais* decoração de texto *mais* fundo. Nunca depende de matiz sozinho. Isto satisfaz WCAG SC 1.4.1 (§3.1) e sobrevive a impressão e screenshot.
2. **As duas camadas coexistem sem colisão porque ocupam canais visuais diferentes** — badge vs dot+decoração. Ambas podem estar ativas no mesmo nó.
3. Persistência **migrou de localStorage para API server-side** (`/v1-update-resource-progress`); a função `clearMigratedRoadmapProgress()` limpa o localStorage legado de 52 roadmaps. Sinal de que progresso anônimo não escala quando o produto vira social.

Hex exatos dos dots: **não verificado** (o CSS não foi recuperável; só os nomes de cor via DeepWiki).

### 1.4 Scrimba — por que o "vídeo" não é vídeo

Vale registrar porque redefine o que "movimento" significa nesta família.

**[FACT]** Per Harald Borgen, fundador: *"We record the underlying events instead of pixels. When replaying a Scrimba screencast, we recreate exactly what the creator did."* Resultado: **~1% do tamanho de arquivo de vídeo** ([SurviveJS](https://survivejs.com/blog/scrimba-interview/)). E: *"We register every keystroke and every interaction you do inside of a scrim and record it all so you can rewind back"* ([Scrimba Podcast 165](https://podcast.scrimba.com/165/transcript)).

Consequências de design:

- **Não existe elemento `<video>`.** O "player" é um editor real cujo buffer está sendo dirigido por um stream de eventos reprisado. É por isso que pausar → editar → rodar funciona sem handoff.
- **O scrubber é semântico, não baseado em frames.** O código em qualquer timestamp é um documento real, editável e executável.
- **"Fork neste ponto"** só existe porque o estado é reconstruível.
- Relevância direta para máquina fraca: **1% do peso de vídeo** é a diferença entre funcionar e não funcionar numa escola.

O pivô visual da v2 é uma lição sobre restrição de tom: *"The editor needs to be very functional in its design to be a good editor… we realized then, okay, let's just embrace that."* **A ferramenta dentro do produto define o teto de quão lúdica a marca pode ser.**

### 1.5 Tipografia — o que está verificado e o que não está

Todas as três grandes plataformas de consumo encomendaram tipo próprio ou semi-próprio. Isso trata tipografia como infraestrutura de marca, não escolha de estilo.

| Plataforma | Fonte | Status |
|---|---|---|
| Duolingo | **Feather / Feather Bold** — foundry Fontsmith, direção Phil Garnham, via Johnson Banks (2019); desenhista creditada Krista Radoeva. Letras derivadas da asa do Duo | **Verificado** ([Monotype](https://www.monotype.com/resources/duolingo-custom-font-inspired-their-owl-mascot-duo), [Creative Bloq](https://www.creativebloq.com/news/feather-bold), [Fonts In Use](https://fontsinuse.com/uses/59497/duolingo-app)) |
| Duolingo (UI) | DIN Next Rounded | **Não verificado** — só agregadores de fonte |
| Khan Academy | **Chalky** — bespoke, display/anotação, uso parcimonioso. Sistema consolidado de 8+ faces para 5, e de 119+ estilos para 14, *"in conjunction with our grid system to ensure a more comfortable line length"* | Consolidação **verificada**; "Chalky" via snippet de `brand.khanacademy.org` (o domínio deu 404 no fetch direto) |
| Khan Academy (corpo) | Lato / Source Serif Pro | **Não verificado** — não citar |
| Brilliant | **CoFo Robert** (headers) + **CoFo Sans** (produto, versão levemente customizada da Contrast Foundry) | **Verificado, first-party** — [Peter Cho, VP de Design](https://pcho.medium.com/a-brilliant-brand-refresh-4af021c11486) |
| freeCodeCamp | Mono **Hack-ZeroSlash**, proporcional **Lato**, logo **SaxMono**. **Mínimo 18px** | **Verificado** ([design-style-guide](https://design-style-guide.freecodecamp.org/)) |
| Coursera | **Source Sans Pro** + **Noto Sans Pro** — escolhidas porque *"support 582 languages and provide optimal upload and download speeds across devices"* | **Verificado, first-party** ([blog.coursera.org](https://blog.coursera.org/evolving-courseras-brand-identity/)) |
| Coursera (cores) | #0056d2 etc. | **Não verificado** — só engenharia reversa de terceiro; o post oficial **não publica hex** |

Nota sobre a Coursera: a justificativa declarada para a escolha tipográfica é **cobertura de idiomas e velocidade de download**, não estética. É o argumento de tipografia mais alinhado a este projeto de toda a pesquisa.

### 1.6 Design systems reutilizáveis

| Sistema | Dono | Licença / uso | Observação |
|---|---|---|---|
| **Wonder Blocks** | Khan Academy | **MIT** ([repo](https://github.com/Khan/wonder-blocks)) | React + TypeScript. O README diz *"We are not accepting external contributions at this time"* — isso é sobre **contribuição**, não sobre uso; a licença MIT permite o uso. O sistema de tokens de cor é a peça mais valiosa (§2.3) |
| **Gamut** | Codecademy | [repo público](https://github.com/Codecademy/gamut) | 96 componentes, React+TS, `variance` CSS-in-JS. Pacotes incluem `gamut-illustrations` e `gamut-patterns` — ilustração como primitiva de primeira classe. Usa o addon de acessibilidade do Storybook |
| **@freecodecamp/ui** | freeCodeCamp | [docs](https://contribute.freecodecamp.org/how-to-work-on-the-component-library/) | React + TailwindCSS + Storybook. Duas camadas de token (base `gray00` → semântica `foreground-primary`); componentes **obrigatoriamente** estilizados para tema claro e escuro |
| **Tufte CSS** | — | **MIT** | Ver §6.4. CSS puro, zero JS |

---

## 2. Os padrões recorrentes — o que define a família

Destilado do que aparece em quase todas e **não** aparece nas outras três famílias.

### 2.1 O próximo passo é sempre visível — e há três escopos distintos

Não é um padrão único. É a mesma promessa resolvida em três escalas, e a escolha importa.

| Escopo do "próximo" | Mecanismo | Exemplo |
|---|---|---|
| Próxima **posição** | Bookmark server-side que restaura onde parou, atravessa dispositivos e sobrevive a meses de ausência | Coursera **"Resume"** — *"takes you back to where you last left off—even if it was in the middle of watching a video"* |
| Próxima **decisão** | Emergente do estado renderizado; não existe botão "próximo" | roadmap.sh — o próximo é qualquer nó ainda `pending` |
| Próximo **keystroke** | O meio se interrompe sozinho | Scrimba **auto-pause no desafio**: *"we auto pause for you and force you to actually get your hands on the keyboard"* |

**O mecanismo do roadmap.sh merece destaque porque é o mais barato de construir e o mais fácil de errar.** Ele funciona porque itens concluídos são **visualmente subtraídos** (tachado + fundo cinza), de modo que os restantes saltam por contraste. Um checkmark verde *adicionado* aos concluídos **não** produziria o mesmo efeito — adicionaria ruído em vez de removê-lo.

> **Regra derivada:** progresso se mostra subtraindo o que já foi, não somando marcas ao que já foi.

### 2.2 A sensação de avanço vem de estado persistente e granular, não de porcentagem

Todas as dez mantêm progresso entre sessões e o expõem numa posição fixa. O que varia é a **granularidade** e ela decide a sensação:

- Granularidade fina + estado nomeado (Khan: attempted/familiar/proficient/mastered) → a pessoa sabe *o que* melhorou.
- Granularidade grossa + porcentagem (Coursera: barra por curso) → a pessoa sabe *quanto falta*, mas não o que sabe.
- A Khan justifica a escolha por retenção: *"learners who work on a skill until a high assessment score is achieved will have better long-term retention"*, e recomenda **explicitamente ir fundo em menos habilidades** em vez de avançar raso por muitas ([blog.khanacademy.org](https://blog.khanacademy.org/why-khan-academy-will-be-using-skills-to-proficient-to-measure-learning-outcomes/)).

Um segundo mecanismo aparece em várias: **decaimento**. A Duolingo tem um anel de progresso por unidade que **decai com o tempo** para provocar revisão. Isto converte progresso de "acúmulo" para "manutenção" — pedagogicamente correto (espaçamento), mas é exatamente onde a família derrapa para o anti-padrão (§4.1).

### 2.3 Cor faz três trabalhos, e a família exige que se declare qual

Nas outras famílias, cor é sinal (B2B/dados) ou marca (consumo). Aqui há **três** papéis possíveis, e a confusão entre eles é o erro característico:

1. **Sinal de estado** — certo/errado, aprovado/reprovado.
2. **Estado de progresso** — pendente/estudando/concluído.
3. **Identidade de assunto** — cor por tópico/track/linguagem.

Quem faz o quê: Brilliant e Exercism usam cor como identidade de assunto; roadmap.sh separa progresso (dot) de autoria (badge); Duolingo funde marca e sinal de acerto.

**A Khan Academy abandonou explicitamente o papel 3.** Reduziram a paleta de **58 para 18 cores** e trocaram codificação por área de assunto por codificação funcional: *"blue denotes action, red and green are accompanied by text to connote warnings or affirmative messaging"* ([designsystems.com](https://www.designsystems.com/about-wonder-blocks-khan-academys-design-system-and-the-story-behind-it/)).

O esquema de token deles tem quatro partes — **Domain → Layer → Context → Intensity** (ex.: `Core.Background.Instructive.Subtle`) — com regras de contraste explícitas: Strong Foreground passa **4.5:1+** sobre todos os Background Subtle e Base; Background Default e Strong passam **3:1+** sobre Background Base Default e Subtle ([blog.khanacademy.org](https://blog.khanacademy.org/how-we-rebuilt-khan-academys-color-system-from-the-ground-up)). Nenhum hex é publicado no artigo — **não usar hex de Khan a partir desta pesquisa.**

**Contraste direto que vale a decisão:** a Khan **exige texto junto de vermelho/verde**. A Duolingo usa vermelho/verde com **áudio** redundante — o que a própria comunidade documenta como lacuna de acessibilidade para deuteranomalia, sem modo oficial de daltonismo ([FAQ de acessibilidade da comunidade](https://duolingo.fandom.com/wiki/Frequently_asked_questions/Accessibility)). **A regra da Khan é a defensável**, e é literalmente WCAG SC 1.4.1 (§3.1).

### 2.4 A celebração é atrelada ao acerto e dosada — e há um tipo de feedback só para ela

Onde a celebração aparece, nas dez: **no momento do acerto**, dentro da lição, não numa tela separada. Duolingo dá a cada personagem *"a unique animation that would play anytime a learner answered an exercise correctly"*, mais animações de meio de lição como recompensa por **acertos consecutivos** ([blog.duolingo.com](https://blog.duolingo.com/building-character/)).

**Ela orienta ou apenas premia?** A resposta honesta é: majoritariamente premia. A exceção instrutiva é a **Exercism**, que tem uma taxonomia de comentários em que uma das quatro categorias é `celebratory` — *"tell users they've done something right"* — com tratamento de UI distinto e **nenhuma ação sugerida** ([interface de analyzers](https://exercism.org/docs/building/tooling/analyzers/interface)):

| Tipo | Efeito |
|---|---|
| `essential` | **soft-block** até ser endereçado |
| `actionable` | encoraja resolver antes de concluir |
| `informative` | informa, nenhuma ação (default) |
| `celebratory` | reconhece acerto, nenhuma ação |

Este é o design de feedback mais transferível do conjunto: **celebração como um tipo de feedback tipado, não como um efeito visual**. Torna a celebração dosável e desligável por regra, não por gosto.

A Exercism também define um **piso de reconhecimento** para mentores: *"If there is nothing you can honestly praise about their solution, you can congratulate them on passing the tests"* — e um teto: *"Give the most important one to three pieces of feedback on any iteration"* ([como dar bom feedback](https://exercism.org/docs/mentoring/how-to-give-great-feedback)).

### 2.5 O erro é reformulado, não punido — nenhuma das dez remove progresso por errar

Este é o padrão mais consistente e o mais distante das outras famílias. Nas dez plataformas, **nenhuma remove progresso por errar**. O que varia é o que se oferece no lugar.

| Plataforma | Tratamento do erro |
|---|---|
| **freeCodeCamp** | **Diff esperado/real**: tokens `--fcc-expected--` e `--fcc-actual--` são substituídos pelos valores da assertion que falhou. Testes mínimos por design: *"Challenges should have the minimum number of tests necessary"*. Hints são **fora do produto** (botão leva ao fórum); na versão nova, *"context-specific hints"* que *"subtly point you in the right direction without completely giving away the answer"* |
| **Exercism** | Analyzers + **Representers** (normalizam a solução removendo comentários e substituindo nomes por placeholders, para que um feedback canônico humano seja reaproveitado em toda solução equivalente). Só `essential` bloqueia, e é **soft-block** |
| **Codecademy** | Escada explícita: erro explicado → hints no rodapé → **"Get Unstuck"** (revisão de conceito, código-solução, **diff** contra sua solução) → assistente de IA *"to unpack your mistakes"* |
| **Boot.dev** | Não pune o erro; **precifica a ajuda**. Falar com o Boots antes de concluir custa 1 item ou **50% do XP da lição**; depois de concluir é grátis. O tutor *"has been trained to not give you the answer"*, método socrático. Justificativa: IA *"short-circuit[s] the struggle that makes the understanding stick"* |
| **Duolingo** | Verde/vermelho + áudio; personagem reage |
| **Khan Academy** | Vermelho/verde **sempre acompanhados de texto** |

**A regra de redação de feedback da Exercism é o artefato mais diretamente copiável de toda a pesquisa** ([comments](https://exercism.org/docs/building/tooling/analyzers/comments), [mindset](https://exercism.org/docs/mentoring/mindset)):

- Proibido **"just, simply, obviously"** — *"can come across as condescending"*.
- *"Be neutrally observational; avoiding charged statements and blanket statements."*
- Recomendação **antes** da explicação; ordenar por importância.
- Forma do hint, exemplo literal da doc: em vez de *"Write `b = a ? 1 : 2` instead"*, usar *"I think you could reduce the Lines 10-14 down to one line using the Ternary Operator. How might that look?"* — **e alerta que hint vago demais frustra** (*"Reduce lines 10-14 to one line"*).
- Contra positividade tóxica: dizer *"I know you can figure it out"* pode soar dispensivo.
- Enquadramento: *"Conversations tend to be more productive when they are approached as two peers discussing a topic, rather than one person showing off their knowledge to another."*
- *"Exercism focusses on the learning journey, not the destination."*

Isto tem lastro em pesquisa. Shute (2008): feedback formativo eficaz é **não-avaliativo, de apoio, oportuno e específico**; alunos que recebem a resposta correta **com explicação de por que está correta** melhoram mais do que os que só recebem a resposta; e ela **desaconselha** dicas progressivas que sempre terminam entregando a resposta (§6.2).

### 2.6 Vocabulário de jogo e visual de jogo são decisões independentes

Achado que evita um erro caro. A **freeCodeCamp** descreve o próprio ciclo como *"core gameplay loop"* e chama os projetos de certificação de **"miniboss"** ([redesign RWD](https://www.freecodecamp.org/news/responsive-web-design-certification-redesigned/)) — **sem nenhuma iconografia de jogo**. O **Boot.dev** tem a iconografia inteira (XP, nível, boss, guild, baú).

**Dá para ter o enquadramento motivacional de jogo sem a estética de jogo.** Para uma plataforma que precisa parecer material didático e não brinquedo, esta é a saída.

---

## 3. Acessibilidade e inclusão

> Esta seção separa **obrigatório** de **ornamento**. O critério de "obrigatório" adotado aqui é **WCAG 2.2 Nível AA**, que é a baseline legal na maioria das jurisdições e o alvo declarado pelas plataformas sérias.

### 3.1 O piso não-negociável (verificado diretamente no W3C)

| Requisito | SC | Nível | Valor exato |
|---|---|---|---|
| **Cor nunca sozinha** | [1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | **A** | *"Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element."* |
| **Contraste de texto** | [1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | **AA** | **4.5:1** texto normal; **3:1** texto grande |
| Definição de "texto grande" | 1.4.3 | AA | **≥18pt**, ou **≥14pt bold** (≈24px e ≈18,5px, a 1pt = 1,333px) |
| Exceções de contraste | 1.4.3 | AA | texto incidental (UI inativa, decoração pura, texto invisível) e **logotipos** |
| **Contraste reforçado** | 1.4.6 Contrast (Enhanced) | AAA | **7:1** |
| **Alvo de toque** | [2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | **AA** | **24 × 24 CSS px** |
| Exceções de alvo | 2.5.8 | AA | spacing (círculo de 24px centrado não intersecta outro alvo), equivalent, inline, user agent control, essential |
| **Alvo de toque reforçado** | 2.5.5 Target Size (Enhanced) | AAA | **44 × 44 CSS px** |
| **Largura de linha** | [1.4.8 Visual Presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html) | AAA | **máx. 80 caracteres** (40 se CJK); entrelinha ≥1,5; espaço entre parágrafos ≥1,5× a entrelinha; **texto não justificado** |

Notas de leitura:

- **1.4.1 é Nível A.** É o piso do piso, e é exatamente o que separa a solução do roadmap.sh (dot + tachado) e da Khan (vermelho/verde + texto) da solução da Duolingo (vermelho/verde + áudio). Para uma plataforma escolar, **1.4.1 não é negociável**.
- **1.4.8 é AAA**, ou seja, tecnicamente ornamento pelo critério AA. Mas o limite de 80 caracteres coincide com a evidência de legibilidade (§6.3) e o custo de implementar é `max-width` numa regra CSS. **É o ornamento de maior retorno da lista** — trate como obrigatório por decisão própria, não por norma.
- **2.5.8 (24px) é AA; 2.5.5 (44px) é AAA.** Os números de plataforma diferem dos dois — ver o que o agente de acessibilidade levantou em §3.2.

Um item adicional que a pesquisa trouxe e vale como alerta de implementação: o SC 1.4.11 (Non-text Contrast, **AA**, **3:1** para componentes de UI e objetos gráficos) diz explicitamente que valores computados **não devem ser arredondados** — *"2.999:1 would not meet the 3:1 threshold"*. Não confiar no arredondamento do DevTools.

### 3.2 Leitor de tela — o que é mandatório

O erro comum é tratar acessibilidade de leitor de tela como "adicionar ARIA". A maior parte é Nível **A** e sai de HTML correto.

**Nível A — inegociável:**

| SC | Nome | O que exige na prática |
|---|---|---|
| **1.3.1** | Info and Relationships | HTML semântico: `<nav>`, `<main>`, `<h1..h6>`, `<table>` com `<th>`, `<label>` ligado ao input |
| **2.1.1** | Keyboard | tudo operável só por teclado |
| **2.1.2** | No Keyboard Trap | modal/menu não prende o foco |
| **2.4.1** | Bypass Blocks | **skip link** (ou landmarks/headings como técnica alternativa) |
| **2.4.2** | Page Titled | `<title>` descritivo por página |
| **2.4.3** | Focus Order | ordem de foco preserva significado |
| **2.5.3** | Label in Name | nome acessível contém o texto visível do rótulo |
| **3.2.1 / 3.2.2** | On Focus / On Input | receber foco ou mudar campo não muda contexto sozinho |
| **3.3.1 / 3.3.2** | Error Identification / Labels or Instructions | erro identificado **em texto**; todo campo rotulado |
| **4.1.2** | Name, Role, Value | nome/papel/valor expostos à tecnologia assistiva — o SC que ARIA existe para cumprir |

**Nível AA:** 1.4.4 Resize Text · 1.4.10 Reflow · 1.4.12 Text Spacing · 2.4.6 Headings and Labels · 2.4.7 Focus Visible · 2.4.11 Focus Not Obscured · **4.1.3 Status Messages**.

**SC 4.1.3 Status Messages (AA) é o mais fácil de esquecer nesta família.** É o critério que cobre `aria-live` / `role="status"` — ou seja, **todo feedback dinâmico de certo/errado, "salvo", "3 itens restantes"**. Numa plataforma de estudo com correção assíncrona, é o SC mais visível para quem usa leitor de tela e o que quase ninguém implementa.

**SC 1.4.12 Text Spacing (AA)** — os quatro valores que o conteúdo precisa **suportar sem perda** quando o usuário os força:

- `line-height` ≥ **1,5×** o tamanho da fonte
- espaço entre parágrafos ≥ **2×** o tamanho da fonte
- `letter-spacing` ≥ **0,12×** o tamanho da fonte
- `word-spacing` ≥ **0,16×** o tamanho da fonte

### 3.3 Movimento — e a verdade sobre `prefers-reduced-motion`

| SC | Nome | Nível | Regra |
|---|---|---|---|
| **2.2.2** | Pause, Stop, Hide | **A** | movimento/piscar/rolagem que (1) começa automaticamente, (2) **dura mais de 5 segundos** e (3) aparece em paralelo com outro conteúdo precisa de mecanismo de pausar/parar/ocultar |
| **2.3.1** | Three Flashes or Below Threshold | **A** | nada pisca **mais de três vezes em qualquer período de 1 segundo** |
| **2.3.2** | Three Flashes | AAA | mesma regra sem a válvula dos limiares |
| **2.3.3** | Animation from Interactions | AAA | *"Motion animation triggered by interaction can be disabled, unless the animation is essential"* |

Nuance do 2.2.2: conteúdo **auto-updating não tem a exceção de 5 segundos** — *"there is no five second exception for auto-updating since it makes little sense to auto-update for a few seconds and then stop"*. A justificativa dos 5s é ser *"long enough to get a user's attention, but not so long that a user cannot wait out the distraction"*.

**Sobre `prefers-reduced-motion`, a resposta honesta:** é media feature do **W3C Media Queries Level 5** (valores `no-preference` | `reduce`), **Baseline Widely Available desde janeiro de 2020**, suportada em Windows 10/11, macOS, iOS, Android 9+, GNOME e KDE. O Understanding do SC 2.3.3 a cita como técnica suficiente — **mas 2.3.3 é AAA**. Portanto: **respeitar `prefers-reduced-motion` não é requisito AA.**

Custa ~4 linhas de CSS, tem suporte universal há 6 anos, e quem paga o preço de não fazer é o aluno com transtorno vestibular. **Classificação: obrigatório-de-facto por custo/benefício, não por norma.**

### 3.4 Funcionar sem JavaScript — a resposta precisa, não a popular

**Não é requisito da WCAG.** Os Success Criteria são *"written as testable statements that are not technology-specific"*. Não existe SC que diga "funcione com JS desabilitado". O que a WCAG exige é o **Conformance Requirement 5 (Only Accessibility-Supported Ways of Using Technologies)** e o **CR 6 (Non-Interference)** — e JavaScript moderno com ARIA correto **é** accessibility supported.

Tradução: **um SPA em React pode ser 100% WCAG 2.2 AA conforme.** Quem afirma que "sem JS é requisito de acessibilidade" está errado.

**O mandato existe — mas é do GOV.UK, não da WCAG** ([Service Manual](https://www.gov.uk/service-manual/technology/using-progressive-enhancement)):

- *"All government services **must** follow progressive enhancement, even if part of the service or a parent service needs JavaScript"*
- serviços devem ser *"**functional using only HTML**"* — *"a user should be able to navigate through your service using only the HTML"*
- **"Do not build your service as a single-page application (SPA)."** — proibição explícita
- evitar CSS-in-JS *"to ensure styling works if JavaScript fails"*

E o GOV.UK exige WCAG **separadamente**: *"Services must achieve WCAG 2.2 level AA"*. Os dois são requisitos **distintos** no mesmo manual — o que confirma que progressive enhancement é **resiliência, não acessibilidade**.

**Para este caso:** o argumento a favor de funcionar sem JS não é conformidade — é navegador desatualizado, JS que falha no parse, rede de escola derrubando o bundle, e custo de CPU de hidratação em máquina fraca. **Argumento sólido, mas venda-o como performance e resiliência, não como acessibilidade.**

### 3.5 Peso e performance em máquina fraca

**Core Web Vitals**, todos medidos no **percentil 75 de carregamentos**, segmentado entre mobile e desktop:

| Métrica | Good | Needs improvement | Poor |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | **≤ 2,5 s** | 2,5 – 4,0 s | > 4,0 s |
| **INP** (Interaction to Next Paint) | **≤ 200 ms** | 200 – 500 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | **≤ 0,1** | 0,1 – 0,25 | > 0,25 |

FID foi aposentado; INP virou Core Web Vital estável em 2024.

**Performance budgets publicados** ([web.dev, *Performance budgets 101*](https://web.dev/articles/performance-budgets-101)):

- *"Under **170 KB** of critical-path resources (compressed/minified)"*
- *"Under **5 s** Time to Interactive"*
- base de cálculo: *"real-world baseline devices and **3G network speed**"*
- exemplo do próprio artigo: home deve *"load and get interactive in < 5 s on slow 3G on a Moto G4 phone"*

Dispositivo de referência mudou: o Chrome usou o **Moto G4** como baseline global por anos; no **Lighthouse 10** passou para um **Moto G Power emulado** (fonte secundária: [CSS Wizardry, 2025](https://csswizardry.com/2025/08/low-and-mid-tier-mobile-for-the-real-world-2025/)).

**Não verificado:** nenhum budget de performance publicado especificamente para contexto **educacional/escolar**. Os 170 KB de critical-path são a referência mais próxima, e são genéricos.

**Regra derivada para este caso:** medir no p75 do hardware **da escola**, não do laptop de quem desenvolve. Um p75 medido na máquina errada é um número inventado.

### 3.6 Tipografia para dislexia — onde a resposta popular e a correta divergem

Esta é a seção em que a evidência contraria o que se repete.

**O que estudos controlados encontraram:**

| Estudo | Desenho | Achado |
|---|---|---|
| **Wery & Diliberto (2017)**, *Annals of Dyslexia* 67(2):114–127 | single-subject alternating treatment; **OpenDyslexic vs Arial vs Times New Roman**; letter naming, word reading, nonsense word reading | *"Results from this alternating treatment experiment show **no improvement in reading rate or accuracy** for individual students with dyslexia, as well as the group as a whole."* **Nenhum participante preferiu** OpenDyslexic. Conclusão: *"there may be no benefit for translating print materials to this font"* |
| **Kuster et al. (2018)**, *Annals of Dyslexia* 68:25–42 | fonte **Dyslexie** vs Arial; exp. 1 com **n=170** crianças disléxicas; exp. 2 com **n=102** disléxicas + **n=45** não-disléxicas | Sem ganho de velocidade nem precisão. **A maioria preferiu Arial**, e a preferência não se correlacionou com desempenho. *"the Dyslexie font **neither benefits nor impedes** the reading process"* |
| **Rello & Baeza-Yates (2013)**, *Good Fonts for Dyslexia*, ASSETS '13 | eye-tracking, **48 sujeitos disléxicos**, 12 textos em 12 fontes | *"**Sans serif, monospaced and roman font styles significantly improved the reading performance over serif, proportional and italic fonts.**"* OpenDyslexic **não** melhorou tempo de leitura nem reduziu fixações |

**Síntese honesta:** o que tem suporte experimental é o **estilo** (sans-serif, evitar itálico), não a existência de uma fonte especializada mágica. Duas fontes "para dislexia" foram testadas em desenhos independentes na mesma revista e deram **nulo**; uma terceira linha metodológica (eye-tracking) chegou ao mesmo lugar. **A convergência é forte.**

Contraponto que existe e deve ser registrado: há relato de estudo com **adultos** disléxicos onde OpenDyslexic não afetou velocidade mas melhorou **compreensão**. Encontrado apenas em síntese secundária, **citação primária não localizada — não usar como base de decisão**.

**O que a British Dyslexia Association recomenda** ([BDA Dyslexia Style Guide 2023](https://lbhfinspirehub.com/wp-content/uploads/2024/05/BDA-Style-Guide-2023.pdf); o PDF no CDN oficial da BDA devolve 403 — lido em mirror com cabeçalho e rodapé institucionais íntegros, charity 289243):

- *"Use **sans serif fonts, such as Arial and Comic Sans**"*; alternativas: Verdana, Tahoma, Century Gothic, Trebuchet, Calibri, Open Sans
- tamanho **12–14pt ou equivalente (1–1,2em / 16–19px)**
- tracking maior, *"ideally around 35% of the average letter width"*; espaço entre palavras ≥ **3,5×** o espaço entre letras
- entrelinha **1,5 / 150%**
- ***"Avoid Underlining and italics"*** — *"Use bold for emphasis"*
- evitar caixa alta em texto corrido
- headings **≥20% maiores** que o texto normal
- *"Use **dark coloured text on a light (not white) background**"*; *"White can appear too dazzling. **Use cream or a soft pastel colour**"*
- ***"Avoid green and red/pink, as these colours are difficult for those who have colour vision deficiencies"***
- ***"Left align text, without justification"***; evitar múltiplas colunas
- *"Write short simple sentences: **60 to 70 characters is optimal**"*

**Status desta fonte, dito com clareza:** o guia da BDA **não cita nenhum estudo**; apresenta-se como "principles". A recomendação de **Comic Sans** é um bom marcador do gênero — é escolha de advocacy, não de literatura experimental. **Trate como guideline de organização de advocacy.** O subconjunto que **coincide** com achado experimental é: sans-serif, evitar itálico, entrelinha maior, alinhamento à esquerda, medida de linha curta. Note também que a recomendação de 60–70 caracteres bate com §6.3 e com o SC 1.4.8, por caminhos independentes.

**Recomendação derivada:**

- **Fazer:** sans-serif de sistema, base **≥16px**, `line-height: 1.5`, alinhado à esquerda **sem justificação**, medida ~60–70 caracteres, fundo levemente off-white em vez de `#FFF` puro, ênfase em **bold** e nunca em itálico longo, sem caixa alta em blocos.
- **Não fazer:** embarcar OpenDyslexic como default. Custa dezenas de KB de webfont em máquina fraca por um efeito que dois estudos independentes mediram como nulo.
- **Se quiser cobrir os dois lados:** oferecer OpenDyslexic como **toggle opcional**, servido só quando escolhido. Respeita preferência individual sem impor peso nem alegar eficácia que a evidência não sustenta.

### 3.7 Obrigatório vs ornamento — o corte

**Obrigatório (WCAG 2.2 A + AA):** tudo em §3.1, §3.2 e os SCs A de §3.3. Os que mais mordem numa plataforma de estudo: 1.4.1 (cor nunca sozinha), 1.3.1 (semântica), 4.1.2 (name/role/value), **4.1.3 (live regions para feedback de certo/errado)**, 2.1.1/2.1.2 (teclado), 2.4.1 (skip link), 2.4.7/2.4.11 (foco visível e não obscurecido), 3.3.1/3.3.2 (erro em texto, campo rotulado), 1.4.3 (4,5:1), 2.5.8 (24px).

**Obrigatório-de-facto — não é norma, mas é indefensável omitir aqui:**

- `prefers-reduced-motion` (AAA por norma, 4 linhas de CSS na prática)
- alvos de **44–48px** em vez dos 24px do piso — satisfaz WCAG AA, Apple HIG (**44pt**), Material (**48dp**) e o AAA 2.5.5 de uma vez; a doc do Material argumenta que alvos maiores acomodam *"children with developing motor skills"*
- coluna de leitura ≤80 caracteres (1.4.8, AAA por norma)
- LCP ≤2,5 s / INP ≤200 ms / CLS ≤0,1 no p75 **do hardware da escola**
- budget de JS crítico na casa de **170 KB**

**Ornamento — não confundir com acessibilidade:** contraste AAA 7:1 em toda a interface, modo de alto contraste customizado, dark mode, temas por preferência, leitura em voz alta própria (o leitor de tela do SO já faz), toggle de OpenDyslexic.

> Exceção que eu adotaria: **7:1 (SC 1.4.6, AAA) no corpo de texto**. É barato e compra margem real em monitor TN velho de laboratório com gamma ruim. É o único AAA que recomendo como default.

### 3.8 Base legal — depende de onde a escola está

- **Brasil:** Lei 13.146/2015 (LBI), **Art. 63** — obrigatória a acessibilidade nos sítios mantidos por empresas com sede ou representação comercial no país **ou por órgãos de governo**, *"conforme as melhores práticas e diretrizes de acessibilidade adotadas internacionalmente"*; §1º exige símbolo de acessibilidade em destaque. A lei **não nomeia versão de WCAG**; o **eMAG** é a especialização brasileira, obrigatória para sites governamentais, baseada em WCAG 2.0.
  - ⚠️ `planalto.gov.br` devolveu `ECONNRESET` nas tentativas de fetch; o texto do Art. 63 veio de síntese de busca. **Confirmar o literal antes de citar juridicamente.**
  - Se a escola for pública, o Art. 63 alcança. Se for projeto de sala de aula sem representação comercial, o enquadramento é discutível — mas o padrão técnico de referência continua sendo WCAG.
- **EUA:** regra final do DOJ sob **ADA Title II** (24/04/2024) exige **WCAG 2.1 AA** para sites de escolas públicas, com prazos escalonados e um Interim Final Rule de 20/04/2026 estendendo-os em um ano. ⚠️ **Datas vindas de fontes secundárias de compliance, não do Federal Register.**
- **Reino Unido:** GOV.UK — *"Services must achieve WCAG 2.2 level AA"*.

**Conclusão prática: um alvo só — WCAG 2.2 nível AA.** É superconjunto do 2.1 AA exigido pelo ADA, igual ao do GOV.UK, e satisfaz o "melhores práticas internacionais" do Art. 63.

### 3.9 O que as plataformas realmente fazem

| Plataforma | Postura de acessibilidade |
|---|---|
| **Codecademy** | **A mais operacional.** Cada painel do ambiente é *"an ARIA Region on the page"* com *"a visually hidden heading on top of it"*, com nomes especificados publicamente: "Narrative", "Code Editor", "Read-only Code Pane", "Output Terminal", "Web Browser". Atalhos para sair do foco do editor (`Escape` ou `Ctrl+M`). **High Contrast mode** (F1) e **Screenreader Mode** (F1, desliga word wrap). Compromisso declarado de acomodar *"auditory, motor, or visual restrictions, limited hardware"* ([artigo](https://www.codecademy.com/article/accessibility-on-the-platform)) |
| **freeCodeCamp** | **Declaração de alvo**, não de mecanismo: WCAG 2.0 Nível A/AA e Section 508. Frase-chave: *"good accessibility is just good usability"*. Admite lacunas: *"our learning platform is still a work in progress"*. **Sem métricas, sem timeline, sem auditoria publicada.** Mas há reforço estrutural: mínimo de **18px** e alto contraste no guia de marca, e a component library exige atenção a *"which HTML elements and ARIA attributes are used under the hood"* ([statement](https://www.freecodecamp.org/news/freecodecamp-accessibility-statement/)) |
| **Khan Academy** | Contraste embutido no sistema de tokens (§2.3); regra red/green + texto; densidade aumentada **justificada por hardware antigo e telas de baixa densidade** |
| **Duolingo** | Depende de áudio redundante para o sinal certo/errado; sem modo oficial de daltonismo. **Lacuna documentada pela própria comunidade** |
| **Exercism** | Nenhum statement encontrado. **Dark mode foi lançado como perk pago** ("UI juice") para Insiders, explicitamente separado do conteúdo educacional, que segue grátis |
| **Boot.dev** | Nenhum statement encontrado |

**Leitura para este caso:** a Codecademy é o modelo a copiar em estrutura (regiões ARIA nomeadas para um layout multi-painel), e a Khan em tokens (contraste garantido por construção, não por auditoria posterior).

---

## 4. Anti-padrões

Ordenados por perigo **para este caso concreto**: acervo de estudo, escola, alunos que não escolheram estar ali, dono que é o professor.

### 4.1 Streak diário e aversão à perda — o mais perigoso porque é o mais copiado

- Streaks exploram **aversão à perda**: perder uma sequência de 200 dias dói mais que ganhar equivalente ([The Decision Lab, "Streak Creep"](https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification)).
- Efeitos relatados na literatura de gamificação: **culpa, ansiedade e checagem compulsiva**; sistemas de feedback gamificado associados a ansiedade, dependência e burnout quando ancorados em streaks, rankings e metas diárias.
- Amplificadores visuais do gênero: urgência escalonada do ícone conforme o dia avança, mascote triste em notificação, monetização do alívio (streak freeze).
- Dado que corta nos dois sentidos: o **streak freeze reduziu churn em 21%** justamente por **aliviar ansiedade** de usuários em risco — a própria empresa mediu que a ansiedade era o problema.

**Correção de fonte que fiz nesta pesquisa:** buscas secundárias afirmam que a Duolingo está catalogada em `deceptive.design`. Fui à página de marca ([deceptive.design/brands/duolingo](https://www.deceptive.design/brands/duolingo)) e **ela não lista nenhuma ocorrência documentada**. A afirmação circula mas **não se sustenta nessa fonte**. Registrado como corrigido, não como fato.

**Por que é o pior para este caso:** o aluno que falta por doença, por prova, ou por não ter computador em casa perde o streak. **O mecanismo pune exatamente a circunstância que a escola deveria absorver** — e o dono do sistema é o professor dele.

Existem gradações menos punitivas, todas verificadas:
- **Codecademy: streak semanal**, não diário — o incremento acontece ao bater a meta da semana.
- **Boot.dev**: streak conta lição **ou** commit no GitHub, com *embers* que absorvem dias perdidos — *"Embers make the 'daily' streak into more of a '5 days a week' streak if you're putting in solid effort"*.
- **Duolingo**: anel de progresso por unidade que decai — a versão pedagogicamente honesta da mesma ideia, porque o que decai é a *revisão devida*, não uma pontuação.

### 4.2 Leaderboard público em turma fechada

Diferente de leaderboard em app de consumo: numa turma, o ranking é entre pessoas que se conhecem e se veem no dia seguinte.

- Ranking público causa **ansiedade e desengajamento** em alunos de menor desempenho; a natureza pública pode **bloquear o senso de pertencimento** de quem está embaixo.
- Alunos que ficam para trás relatam **queda no senso de competência**.
- Um estudo longitudinal quasi-experimental encontrou que leaderboards **não** geraram prática adicional e foram associados a **notas mais baixas** em prova ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1041608024001651)).
- **A evidência é conflitante, não unânime** — há estudos com ganho de engajamento, inclusive entre alunos de menor desempenho. Reporto o conflito porque é o estado real da literatura.
- Mitigação com apoio: **leaderboard relativo** (só os vizinhos de desempenho semelhante) em vez de absoluto.

Precedente relevante: o **Boot.dev tornou os achievements de boss cooperativos** — total de bosses que você ajudou a derrotar, *"no longer competitive"*, com o boss sendo abatido pelo XP da comunidade inteira. **É o padrão social sem o padrão de ranking.**

### 4.3 Celebração e animação que cobram pedágio de quem já sabe

- Padrão medido no gênero: sucesso com confete de 2s + auto-redirect de 1s = **~4,3s de espera forçada**; a versão com skip cai para ~1,2s ([regra dos 3 segundos](https://robertcelt95.medium.com/micro-interactions-that-dont-annoy-the-3-second-rule-for-ui-animation-9881300cd187)).
- NN/g: animação serve a **feedback, mudança de estado, navegação espacial e signifiers**; prejudica quando é **gratuita, distrativa ou manipulativa** — e cita explicitamente movimento como dark pattern (contagem regressiva piscando que dispara aversão à perda) ([NN/g](https://www.nngroup.com/articles/animation-purpose-ux/)).
  - **Nota de fidelidade:** o artigo da NN/g **não** traz números de duração e **não** trata de usuário experiente nem de `prefers-reduced-motion`. O 4,3s vem de outra fonte, de menor peso.
- Boa prática recorrente: tutorial animado só na primeira vez, e sempre pulável.

**Por que dói aqui:** o aluno que revisa 30 itens seguidos paga a animação 30 vezes. **Em máquina fraca, paga duas vezes** — no tempo de espera e no frame rate. E a arquitetura que torna isso viável nas grandes não é trivial: a Duolingo mantém arquivos Rive **abaixo de 1 MB** usando State Machine, com 8 animações de cabeça × 8 de corpo gerando 60+ variações ([Rive](https://rive.app/blog/duolingo-s-ai-powered-video-call-brings-lily-to-life)). **Copiar o visual sem a arquitetura entrega uma fração da variação pelo custo inteiro.**

### 4.4 Gamificação sem calibração de dificuldade

- Pesquisa de UX sobre gamificação: dificuldade mal calibrada produz **desamparo aprendido** (difícil demais) ou **tédio** (fácil demais).
- Modelos de tipo-de-jogador vindos de games online **não** descrevem bem motivação em contexto educacional — as dimensões relevantes são outras (social vs individual, utilidade vs realização).

**Consequência:** copiar mecânica de jogo sem calibrar dificuldade importa o vício sem a virtude.

### 4.5 Nagging / notificação persistente

- `Nagging` é padrão enganoso catalogado: insistir repetidamente mesmo após recusa ([deceptive.design/types/nagging](https://deceptive.design/types/nagging/)).
- Numa escola, notificação de estudo emitida pelo sistema do professor tem **peso coercitivo** que a mesma notificação não teria num app voluntário.

### 4.6 Cobrar por acessibilidade

Registro como anti-padrão porque um dos casos estudados o pratica: a **Exercism lançou dark mode como perk pago**, classificado pela própria empresa como *"UI juice"*, disponível só para Insiders nos primeiros 3 meses ([insiders-preview](https://exercism.org/blog/insiders-preview)). Para um público adulto voluntário, é uma decisão de posicionamento defensável. **Numa escola, colocar qualquer acomodação visual atrás de qualquer barreira é inaceitável** — o aluno que precisa dela é justamente o que não vai pedir.

---

## 5. GitHub Education

> ⚠️ **Alta sensibilidade a data.** Consultado em **2026-08-02**. Ofertas do Student Pack mudam sem aviso, e há uma descontinuação com prazo curto (§5.3). Trate qualquer oferta específica como perecível.

Nota: `education.github.com` **redireciona (302)** para `github.com/education`.

### 5.1 Os quatro programas e quem pode entrar

| Programa | O que dá | Elegibilidade |
|---|---|---|
| **Student Developer Pack** | Dezenas de ofertas de parceiros + GitHub Pro + Codespaces | Matriculado em programa que concede grau ou diploma — *"high school, college, university, or **homeschool**"*; **≥13 anos**; conta pessoal; prova de matrícula atual |
| **GitHub Education for Teachers** | **GitHub Team gratuito com usuários e repositórios privados ilimitados**; dashboard do Classroom; **Copilot Pro** para professores verificados; Campus TV; swag | Docente em instituição acreditada; verificação por e-mail institucional + documentação de vínculo |
| **GitHub Campus Program** | Pacote premium para a instituição inteira | Escola que concede graus/diplomas/certificados; **acordo assinado pelo CIO ou CTO**; a escola precisa oferecer acesso a todos os departamentos técnicos e acadêmicos, exibir o logo no site do GitHub e manter canal de comunicação. Licenças usáveis por TI, pesquisa, colaboradores e alunos **desde que não haja lucro** |
| **GitHub Skills** | Cursos interativos | Aberto |

**Documentação aceita para aluno:** carteirinha com data de matrícula vigente, grade horária, histórico, ou carta de vínculo. **O processo é individualizado por escola** — se candidatos anteriores da mesma escola se verificaram com e-mail acadêmico, os próximos **precisam** fazer o mesmo.

### 5.2 O que há no Pack hoje que serve a este projeto

Snapshot de `education.github.com/pack` em **2026-08-02**:

| Categoria | Ofertas relevantes |
|---|---|
| **Hosting / infra** | **Azure** — 25+ serviços grátis + **US$100** de crédito (18+); faixa 13–17 recebe App Services, Functions e MySQL · **Heroku** — **US$13/mês por 24 meses** · **DigitalOcean** — US$200 "through mid-2026" ⚠️ possivelmente expirado, confirmar · **Appwrite** — plano Education grátis |
| **Domínios** | **Namecheap** — um `.me` grátis por 1 ano + 1 SSL grátis por 1 ano · **Name.com** — um domínio grátis entre 25+ extensões (`.dev`, `.app`, `.live`…) · **.TECH** — um domínio grátis por 1 ano |
| **Dev / CI** | **GitHub Pro** durante os estudos; **Codespaces** nível Pro (⚠️ a página indica que **novas inscrições com Copilot estão pausadas**) · **Travis CI** · **JetBrains** (1 ano) · **GitKraken** / **GitLens** (6 meses) |
| **Monitoramento** | **Sentry** — 50 mil erros, 100 mil transações, 1 GB de anexos por 1 ano · **Datadog** — Pro para 10 servidores por 2 anos · **New Relic** · **Codecov** — públicos e privados |
| **Design / UI** | **Polypane** (1 ano) · Bootstrap Studio · Icons8 (3 meses) · IconScout · Visme |
| **Aprendizado** | Boot.dev (3 meses), Scrimba (1 mês Pro), FrontendMasters (6 meses), Educative, DataCamp, GoRails |

**Stack mínima viável tirada só do Pack:** Name.com ou Namecheap (domínio) + Azure ou Heroku (hosting) + Sentry (erros) + Codecov (cobertura) + GitHub Actions (CI, já no Pro).

**A peça mais subestimada do Pack para este caso é o Polypane** — ferramenta de teste responsivo e de acessibilidade. Conversa diretamente com tudo em §3, e é justamente o tipo de licença que ninguém compra num projeto pessoal.

### 5.3 ⚠️ GitHub Classroom está sendo descontinuado

Achado mais importante desta frente, e ele invalida qualquer plano baseado em Classroom:

| Data | Evento |
|---|---|
| **22/05/2026** | Anúncio oficial. *"Starting today, new sign-ups for GitHub Classroom are no longer available as we transition to partner solutions"* ([GitHub Changelog, 26/05/2026](https://github.blog/changelog/2026-05-26-github-classroom-sign-ups-are-no-longer-available/)). Rodava em modo manutenção havia 18 meses |
| **28/08/2026** | *"GitHub Classroom will fully transition to partner solutions. After that date, users won't be able to sign in to manage classrooms, and the GitHub Classroom website will be **decommissioned**."* Prazo final de exportação |
| **04/09/2026** | Deleção final dos dados: nomes de classrooms/assignments, testes definidos fora de repos, histórico de test runs, submissões, rosters via LTI |

**Substitutos endossados:**

1. **Codio** — parceiro comercial exclusivo. SSO via LMS, grade passback, detecção de plágio. Instrutor grátis; instituições recebem 50 licenças de aluno de cortesia inicialmente.
2. **Classroom 50** — alternativa **open-source** da Fifty Foundation: CLI + interface web, distribuição de assignments, auto-grading via GitHub Actions.

**Relevância para uma plataforma de estudo self-hosted: baixa, e agora nula como dependência.** Classroom serve para distribuir assignments em repositórios e auto-corrigir via Actions — é ferramenta de aula de programação, não de plataforma de estudo. **Não construir nada em cima dele.** Se o auto-grading via Actions for desejado depois, **Classroom 50** é o único caminho que não prende a fornecedor comercial.

### 5.4 Valor de design — Primer, não GitHub Education

**GitHub Education publica design guidelines próprias? Não encontrei.** O site serve como referência visual informal, não como guideline publicada. O que existe de aproveitável é o **Primer**, design system corporativo do GitHub:

- Três eixos: **Product UI**, **Brand UI**, **Brand Toolkit**. Foundations compartilhadas: **Octicons** (ícones SVG), guidelines de acessibilidade, e primitives de cor, espaçamento e tipografia.
- **Licença MIT**, verificada em `primer/react/LICENSE` e `primer/primitives`. Uso comercial, modificação e distribuição permitidos mantendo o aviso de copyright.
- `@primer/primitives` é publicado no npm como **tokens em JSON + CSS variables** — consumível **sem adotar React**.
- Primer publica guidelines de acessibilidade próprias e declara: *"GitHub aims for Web Content Accessibility Guidelines (**WCAG 2.2**) **AA** conformance."* Cobrem uso de cor, link vs botão, gestão de foco, alt text, movimento/animação, HTML semântico e ARIA, redimensionamento de texto — mais checklists por papel e um annotation toolkit. Abordagem declarada: "shift-left".

**Veredito:** o ativo mais valioso do Primer aqui **não são os componentes — são os primitives de cor**. São pares com contraste já auditado para AA, em light e dark, o que resolve boa parte dos SCs 1.4.3 e 1.4.11 sem trabalho manual, e são consumíveis como JSON puro.

⚠️ **Cuidado com o Brand Toolkit e os logos** — marca registrada não é coberta por licença MIT de código. Não localizei declaração explícita de restrição de trademark, mas presuma que o logo do GitHub não é reutilizável.

### 5.5 Caminho prático para o professor

1. **Verificar primeiro se a instituição já é Campus Program** — se for, o caminho individual é desnecessário.
2. **Professor se verifica em GitHub Education for Teachers** (e-mail institucional + documento de vínculo) → ganha **GitHub Team grátis com repositórios privados ilimitados**, o que cobre hospedagem do código e colaboração dos alunos.
3. **Alunos ≥13 anos aplicam ao Student Pack individualmente** — o professor não aplica por eles.
4. Hospedar com Azure/Heroku e domínio do Name.com, ambos do Pack.
5. **Não planejar com GitHub Classroom.** Fecha em 28/08/2026.

Isso cobre a infraestrutura do projeto a custo zero sem tocar em Classroom.

---

## 6. Base teórica — por que "parecer material didático" tem lastro medido

Esta seção sustenta as escolhas acima contra o gosto pessoal.

### 6.1 Princípio da coerência / seductive details — decoração derruba aprendizado

O achado mais acionável de toda a pesquisa, e o que mais contraria o instinto de "deixar bonito".

- **Princípio da coerência** (Richard Mayer): aprende-se mais quando palavras, imagens e sons irrelevantes são **excluídos**, não quando são adicionados ([Mayer, Principles for Reducing Extraneous Processing](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf)).
- **Seductive details** = informação interessante porém irrelevante ao objetivo instrucional. A meta-análise de **Rey (2012)** encontrou efeito **negativo** em retenção (pequeno a médio) e em transferência (médio) ([The eLearning Coach](https://theelearningcoach.com/learning/seductive-details/)).
- Mecanismo proposto: sobrecarga de memória de trabalho, distração atencional, interferência de esquema, ruptura de coerência.
- O capítulo de Clark & Mayer sobre o tema chama-se literalmente *"Adding Material Can Hurt Learning"* ([PDF](https://alison.com/course/532/resource/file/Chapter_8_Applying_the_Coherence_Principle_-_Adding_Material_Can_Hurt_Learning.pdf)).

**Consequência de direção visual:** nesta família, "enfeitar para engajar" é uma hipótese **falsificada**, não questão de gosto. O critério de pertinência da `visual-direction` ("que pergunta esta seção responde?") ganha versão mais dura: **elemento que não serve ao objetivo de aprendizagem daquela tela é dano, não neutro.**

**Ressalva honesta:** o efeito é medido em material instrucional — a lição em si. Não se estende automaticamente a navegação, perfil ou estado vazio, onde ilustração pode orientar sem competir com conteúdo. **A regra vale onde há algo a aprender na tela.** É exatamente a divisão que a Khan pratica: sem mascote na plataforma principal, elenco completo no Khan Academy Kids.

### 6.2 Feedback formativo — a forma correta de tratar o erro

Valerie Shute, *Focus on Formative Feedback*, Review of Educational Research, 2008 ([PDF](https://myweb.fsu.edu/vshute/pdf/shute%202008_b.pdf)):

- Feedback formativo = informação comunicada ao aluno com intenção de **modificar seu pensamento ou comportamento**.
- O que funciona: **não-avaliativo, de apoio, oportuno e específico**.
- Tipos: verificação de acerto, explicação da resposta correta, dicas, exemplos resolvidos.
- Sobre erro: alunos que receberam a resposta correta **com explicação de por que está correta** melhoraram mais que os que só receberam a resposta.
- Shute **desaconselha** dicas progressivas que sempre terminam entregando a resposta; recomenda prompts e cues que guiam sem revelar.

Isto é exatamente a regra que a Exercism e o Boot.dev implementam (§2.5). **O estado de erro não é um `alert-danger`** — é a superfície com mais trabalho de design da plataforma inteira.

### 6.3 Comprimento de linha — a medida que separa "documento" de "app"

- Convergência entre pesquisa de tipografia e guias de estilo: **45–75 caracteres por linha**, com **66 CPL** como alvo mais citado (origem: Bringhurst) ([Baymard](https://baymard.com/blog/line-length-readability), [Web Typography](http://webtypography.net/2.1.2)).
- Dyson & Haselgrove: ~55 CPL sustenta leitura eficaz em velocidade normal e rápida.
- **Leitor novato vai melhor perto de 45 CPL**; leitor experiente tolera até 80. Relevante direto: o público é novato por definição.
- WCAG SC 1.4.8 (AAA): máximo **80 caracteres**, entrelinha ≥1,5, **texto não justificado** (§3.1).

**Consequência:** uma coluna de leitura limitada — e não a largura toda do viewport — é provavelmente a mudança de maior razão sinal/esforço para um produto que "parece ferramenta". **Ferramenta usa a largura toda; material didático não.**

### 6.4 Explanatory design — a linhagem que a taxonomia não cobre

Polo de referência para "parecer apostila sem parecer app":

- **Tufte CSS** ([repo](https://github.com/edwardtufte/tufte-css)) — tipografia bem ajustada, **sidenotes/margin notes extensas**, integração próxima entre gráfico e texto. **Licença MIT. Somente CSS** — o repo declara soluções JS explicitamente fora de escopo. Descrito como essencialmente completo em features.
  - Valores verificados diretamente no [`tufte.css`](https://raw.githubusercontent.com/edwardtufte/tufte-css/gh-pages/tufte.css): corpo `et-book, Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif`; código `Consolas, "Liberation Mono", Menlo, Courier, monospace`; `@font-face` declara **et-book** (roman line-figures, display italic old-style, bold line-figures) e **et-book-roman-old-style**; parágrafo a **55%** de largura; sidenote a **width: 50%** com `margin-right: -60%`; `max-width: 1400px` no body.
  - **Relevância dupla aqui:** é a estética de apostila **e** é dependency-free — atende o requisito de máquina fraca sem trade-off.
- **Distill.pub** ([guia](https://distill.pub/guide/)) — framework CSS + web components para artigos acadêmicos interativos.
- **Bartosz Ciechanowski** ([CSS-Tricks](https://css-tricks.com/bartosz-ciechanowskis-interactive-blog-posts/)) — posts explicativos com visualizações interativas.

Estes três não são "plataforma" — não têm progresso, conta nem trilha. São o polo de **densidade tipográfica didática** para conteúdo longo. Úteis como eixo de variação: *trilha guiada* vs *apostila navegável*.

### 6.5 Uma coisa por tela — o padrão tem nome e dono

O GOV.UK Service Manual recomenda explicitamente ([form structure](https://www.gov.uk/service-manual/design/form-structure)):

> *"Start by splitting the form across multiple pages with each page containing just one thing, for example: one piece of information you're telling a user, one decision they have to make, one question they have to answer."*

Benefícios declarados — e três dos cinco são diretamente educacionais:

- *"understand what you're asking them to do"*
- *"focus on the specific question and its answer"*
- *"find their way through an unfamiliar process"*
- *"use the service on a mobile device"*
- *"recover easily from form errors"*

Ressalva do próprio GOV.UK: *"User research will tell you when you can merge pages together"* — especialmente para usuários que repetem a tarefa com frequência. **É a mesma tensão do §0: baixa densidade no passo, não no produto.**

Base cognitiva: teoria da carga cognitiva (Sweller, 1988) — a memória de trabalho processa uma quantidade limitada por vez; disclosure progressivo reduz carga **extrínseca** ao remover estímulos competindo com a tarefa primária.

### 6.6 Diátaxis — por que um acervo "parece ferramenta"

Relevante ao diagnóstico específico deste projeto. O [Diátaxis](https://diataxis.fr/) separa documentação em quatro tipos por **necessidade do usuário**:

| Tipo | Orientação | Necessidade |
|---|---|---|
| **Tutorial** | aprendizado | iniciante sendo conduzido, mão na massa |
| **How-to guide** | tarefa | atingir um objetivo específico |
| **Reference** | informação | consultar um detalhe |
| **Explanation** | entendimento | compreender um conceito |

A tese: *"documentation should itself be organised around the structures of those needs."*

**Diagnóstico derivado:** um acervo de estudo compilado por LLM tende a produzir **reference** — verbetes consultáveis. Reference *é* o modo que parece ferramenta, porque atende quem já sabe o que procura. **A sensação de "material didático" vem de tutorial e explanation**, que são os dois modos ausentes por default numa wiki gerada. A correção não é visual antes de ser estrutural: uma trilha de leitura ordenada (tutorial) e verbetes que respondem "por quê" (explanation) mudam mais a percepção do que qualquer escolha de cor.

---

## 7. Linha proposta para a taxonomia da `visual-direction`

Formato da tabela existente no passo 2 da skill:

| Família | Exemplos | O que caracteriza | Serve quando |
|---|---|---|---|
| **Plataforma de educação** | Khan Academy, Brilliant, Exercism, roadmap.sh, Duolingo | Progresso como elemento de primeira classe e persistente; um passo por tela dentro da lição e mapa denso fora dela; cor com papel declarado (estado, progresso ou assunto) **nunca sozinha**; erro tratado como reformulação, não como falha | Quem usa está aprendendo — a tela precisa mostrar o próximo passo e o caminho percorrido, não só executar uma ação |

Eixos que a família acrescenta aos quatro atuais (hierarquia, densidade, cor, movimento, pertinência):

- **Progresso** — qual é a metáfora (caminho, estado de maestria, grafo, credencial), e onde ela vive de forma fixa. Ver §1.2 para o custo de cada uma.
- **Erro** — o que a tela faz quando a pessoa erra. Se a resposta for "fica vermelho", a direção não foi tomada.

---

## 8. Registro do que **não** foi verificado

Lista explícita para que nada daqui vire fato por citação repetida.

**Contradição que a checagem direta corrigiu:**

- Fontes secundárias afirmam que a Duolingo está catalogada em `deceptive.design`. A **página de marca não lista nenhuma ocorrência documentada** (§4.1). Registrado como corrigido.
- A distinção obrigatório/alternativo no roadmap.sh **não** é sólido-vs-tracejado nem preenchimento roxo-vs-cinza — é badge de canto (§1.3). Verificado no export oficial.

**Não verificado — não citar:**

| Item | Situação |
|---|---|
| Hex da Duolingo (Feather Green etc.) | `design.duolingo.com` é JS-rendered; não abriu em fetch. Valores circulam sem citação oficial |
| Hex da Khan Academy | O artigo oficial de cor **não publica hex** — só swatches e razões de contraste |
| Hex da Brilliant, do roadmap.sh, do Exercism, do Codecademy, do Boot.dev | Nenhuma fonte |
| Hex da Coursera (#0056d2 etc.) | Só engenharia reversa de terceiro; o post oficial não publica hex |
| DIN Next Rounded como face de UI da Duolingo | Só agregadores de fonte |
| Lato / Source Serif Pro como faces de corpo da Khan | Só posts de comunidade, idade incerta |
| Motion design da Khan Academy | **Ausência de fonte, não evidência de movimento mínimo** |
| Motion da freeCodeCamp, Exercism, Codecademy | Sem fonte |
| Layout de painéis de Exercism e Boot.dev | Sem fonte |
| Statements de acessibilidade de Exercism e Boot.dev | Não existem, ou não foram encontrados |
| Cor / dark mode default do Boot.dev | Sem fonte |
| N exato do estudo Wery & Diliberto (2017) | Não constava no abstract |
| Estudo de ganho de **compreensão** com OpenDyslexic em adultos | Só síntese secundária; citação primária não localizada |
| Texto do Federal Register (ADA Title II + Interim Final Rule 2026) | Datas vindas de blogs de compliance |
| Texto normativo do eMAG e versão de WCAG base | Só síntese de busca |
| Literal do Art. 63 da Lei 13.146/2015 | `planalto.gov.br` deu `ECONNRESET`; confirmar antes de uso jurídico |
| Budget de performance para contexto educacional | **Não existe publicado**, que eu tenha encontrado |
| Restrição de trademark do Primer Brand Toolkit | Sem declaração explícita localizada; presumir restrito |
| Nome exato do arquivo de fonte `et-book` no CSS | Resolvido — ver §6.4, verificado no CSS |

**Fontes com ressalva de acesso:**

- `brand.khanacademy.org` deu **404** em fetch direto; conteúdo (Chalky, traços de personalidade, estilo de ilustração) veio só de snippets de busca.
- O PDF oficial do BDA Style Guide 2023 devolve **HTTP 403** no CDN da BDA; lido em mirror com cabeçalho e rodapé institucionais íntegros.
- `raw.githubusercontent.com` e a árvore do GitHub deram 404 para o repo do roadmap.sh; o CSS dos dots não foi recuperado.
- `scrimba.com/home` renderizou como shell SPA vazio.

**Como fechar as lacunas restantes, se valer a pena:** Playwright contra o grafo vivo do roadmap.sh, contra o player da Scrimba e contra `design.duolingo.com` resolveria a maior parte dos itens de cor e layout. Nenhum deles é bloqueante para a decisão de direção visual.
