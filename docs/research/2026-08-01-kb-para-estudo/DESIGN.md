# Direção de design — plataforma de estudos

> Para validação do dono. Produzido com a skill `visual-direction`, sobre duas pesquisas de 2026-08-02: `pesquisa-codedex.md` (hex lidos do CSS de produção e do runtime, não estimados de screenshot) e `pesquisa-educacao.md` (padrões da família, com lastro em literatura de aprendizagem).

## O achado que qualifica o pedido

Você pediu para absorver as animações do Codédex. A pesquisa achou um limite medido, e ele muda **onde** elas podem entrar — não se entram.

**Decoração em material instrucional é dano medido, não neutro.** O princípio da coerência de Mayer e a meta-análise de Rey (2012) sobre *seductive details* encontram efeito **negativo** em retenção e em transferência quando se acrescenta material interessante porém irrelevante. O capítulo de Clark & Mayer chama-se literalmente *"Adding Material Can Hurt Learning"*.

A ressalva que a própria pesquisa registrou, e que salva o pedido: **o efeito é medido na lição em si**, não em navegação, perfil ou estado vazio.

Daí a regra que organiza tudo abaixo:

> **A personalidade mora na moldura. A superfície de leitura fica quieta.**

Movimento, cor de marca e celebração vivem no topo, na trilha, no progresso e na revisão. O artigo em si — onde há algo a aprender — não ganha nada que compita com o texto.

## O que o Codédex ensina, e não é o que parece

**A fofura dele é barata.** Três durações no sistema inteiro (`0,1s` físico, `0,2s` estado, `0,3s` layout), zero `cubic-bezier` próprio, `steps(1)` em vez de interpolação suave, **nenhuma biblioteca de animação**. Sem sombra, sem blur, sem raio em 564 de ~750 elementos, sem gradiente. ~48 KB de CSS.

As três micro-interações que valem copiar, todas classificadas como **orientam**, não decoram:

| Interação | Como | Por que orienta |
|---|---|---|
| Botão afunda 4px | `:active` aplica `translateY(4px)` no topo, sombra fica parada, `.1s` | O controle responde fisicamente ao toque |
| Saída pula | `translateY(0 → -10px → 0)`, `.3s ease-out`, ao chegar conteúdo novo | Resolve "aconteceu algo e eu não vi" |
| Toast de conquista | `scale(.8)+opacity 0 → scale(1)`, `.2s`, fixo embaixo | Confirma sem interromper |

**Dois achados estruturais que contradizem o que já construímos:**

1. **O Codédex não tem sidebar em lugar nenhum.** A hierarquia curso → capítulo → exercício é atravessada **por páginas** — banner, acordeão numerado, barra inferior fixa na lição — nunca por uma árvore sempre aberta. Nossa tela atual tem sidebar permanente.
2. **O progresso dele é sempre `N de M`, nunca percentual.** Nossa barra mostra `0%`, que é a forma mais desanimadora possível de dizer "você não começou".

3. **Ele tem um *objeto* de progresso** — `Level 17`, `6995 XP`, `Platinum`, `61 Badges` — uma ficha que pertence à pessoa e faz sentido mostrar a outro aluno. O Educative tem um *relatório* (calendário de atividade), que é privado por natureza. **Quando isto virar social na escola, é o objeto que precisa existir**, não o relatório.

## Os quatro eixos decididos

**Hierarquia** — o olho vai para: (1) o que estudar agora, (2) onde estou na trilha, (3) o conteúdo, (4) as ferramentas. Hoje a sidebar disputa com o artigo; ela precisa recuar quando a leitura começa.

**Densidade** — **baixa no passo, não no produto.** Esta formulação corrige a minha primeira versão. A Khan Academy **aumentou** densidade em 11–26% e justificou por **equidade**: *"users who need our services the most are on low-cost, older hardware and low-density screens"*. Tela arejada demais obriga a rolar, e rolar em máquina fraca com tela pequena é custo. O que fica baixo é a carga do **passo atual**; o produto pode ser denso.

**Cor** — **sinal e estado, não assunto.** Esta também corrige a minha primeira versão, onde eu recomendei cor por tópico. A Khan **abandonou** exatamente isso: reduziu de 58 para 18 cores e trocou codificação por assunto por codificação funcional. E exige texto junto de vermelho/verde — é WCAG SC 1.4.1, Nível A.

O que substitui a cor por assunto vem do roadmap.sh, que roda **dois sistemas ortogonais** na mesma tela: um comunica a estrutura (opinião de quem montou a trilha), outro comunica o estado do leitor. É exatamente o problema de um acervo — estrutura de assunto mais estado de leitura — resolvido sem gastar a paleta.

**Movimento** — só onde orienta, com as três durações do Codédex. `prefers-reduced-motion` respeitado (o Codédex implementa e o trecho é copiável). Toda celebração pulável.

## Paleta — três direções para você escolher

Todas mantêm o que você já definiu: **bege no claro, laranja no escuro**. Elas divergem em *quanto* de personalidade a moldura carrega.

### A — Sóbria (o que existe hoje, refinado)

Bege `#efe7da` / escuro `#191715`, laranja `#f07a32`. Sem fonte display, sem pixel. Personalidade vem de espaçamento e tipografia, não de cromo.

**Aposta:** material didático sério que não infantiliza. Serve tanto ao seu estudo de segurança quanto a um aluno de 16 anos.
**Risco:** pode continuar parecendo ferramenta, que é a queixa de origem.

### B — Moldura lúdica, leitura sóbria (recomendação da pesquisa)

Mesma base bege/laranja e mesmo corpo de texto. Acrescenta na **moldura**: uma fonte pixelada só para números e títulos de trilha (~15 KB), botão que afunda 4px, toast de conquista, cor por tópico.

**Aposta:** o achado central — personalidade na moldura, silêncio na leitura. Ganha a atmosfera sem pagar o custo medido em retenção.
**Risco:** dois vocabulários tipográficos exigem disciplina para não vazar um no outro.

### B2 — Vocabulário de jogo, visual de material didático

Variação da B que a segunda pesquisa abriu. A freeCodeCamp chama o próprio ciclo de *"core gameplay loop"* e os projetos de *"miniboss"* — **com zero iconografia de jogo**. A energia vem da linguagem, não do pixel.

**Aposta:** parecer material didático sério e ainda assim ter a atmosfera, sem carregar fonte display nem estética que envelhece.
**Risco:** depende de escrita boa em cada rótulo; texto morno derruba tudo, e não há cromo para compensar.

### C — Cheia à la Codédex

Adota o vocabulário NES.css (borda em degrau por `box-shadow`, sem raio), fonte pixelada em toda a chrome, XP e badges visíveis, tema escuro dominante.

**Aposta:** identidade forte e memorável, e o objeto de progresso que a escola vai usar.
**Risco:** o Codédex é **dark-only** e a estética pixel tem público; num acervo que mistura CLRS e OWASP pode soar deslocada. E a leitura longa em fonte pixelada é hostil.

## Tipografia

O Educative roda em **zero webfont** — stack de sistema puro. A adaptação honesta para o nosso caso é híbrida:

- **Corpo:** stack de sistema. Zero download, ótima legibilidade, funciona em máquina fraca.
- **Números e títulos de trilha:** **uma** fonte display, ~15 KB, só nas direções B e C.

Escala do Codédex como referência: `48/72 → 32 → 24/36 → 18 → 16 → 14 → 12`, labels em caixa alta com `letter-spacing` generoso.

## O que NÃO vamos copiar — e isto importa mais porque a escola entra

| Anti-padrão | Por quê |
|---|---|
| **Streak diário** | Existem gradações verificadas que o tornam sobrevivível: a Codecademy usa streak **semanal**, e o Boot.dev tem *embers* que absorvem dias perdidos. Sem uma dessas, explora aversão à perda; a literatura relata culpa, ansiedade e checagem compulsiva. **O aluno que faltou por doença, prova ou falta de computador em casa perde a sequência** — o mecanismo pune exatamente a circunstância que a escola deveria absorver. O próprio Duolingo mediu que o *streak freeze* reduz churn em 21% **por aliviar ansiedade** |
| **Ranking público em turma** | Ranking entre pessoas que se veem no dia seguinte. Estudo longitudinal encontrou ausência de prática adicional e associação com **notas mais baixas**. A evidência é conflitante, não unânime — mas o risco é maior aqui porque o dono é o professor. Se houver ranking, que seja **relativo** (vizinhos de desempenho), nunca absoluto |
| **Celebração que interrompe** | Confete de 2s + redirect de 1s dá ~4,3s de espera forçada. **Quem revisa 30 cartões paga 30 vezes** — e em máquina fraca paga no frame rate também |
| **Nav por `<div>` sem `role`** | O Codédex faz isto: os controles de ícone da nav são inalcançáveis por teclado. Para alunos de escola é bloqueante |

## Acessibilidade — requisito, não polimento

Vai para escola: contraste WCAG AA no mínimo, alvo de toque adequado, foco visível, navegação por teclado em tudo, e a página precisa funcionar em máquina fraca. O `prefers-reduced-motion` do Codédex é copiável literalmente.

Três correções que a pesquisa trouxe e que evitam trabalho errado:

- **Funcionar sem JS não é requisito WCAG.** Um SPA pode ser 100% AA conforme. O mandato é do GOV.UK e é sobre **resiliência**, não acessibilidade — o argumento honesto para adotá-lo é desempenho, não conformidade.
- **OpenDyslexic não tem suporte experimental.** Dois estudos independentes na mesma revista deram nulo, e um terceiro com eye-tracking chegou ao mesmo lugar. O que funciona é o **estilo**: sans-serif, evitar itálico, entrelinha 1.5, alinhamento à esquerda sem justificar, 60–70 caracteres por linha. O guia da BDA que recomenda Comic Sans não cita estudo nenhum.
- **`@primer/primitives` é MIT**, distribui tokens em JSON consumíveis sem React, com contraste **já auditado para AA** em claro e escuro. Resolve boa parte dos critérios 1.4.3 e 1.4.11 sem trabalho manual.

**Aviso com prazo:** o **GitHub Classroom fecha em 28/08/2026**, com deleção de dados em 04/09. Não construir nada sobre ele.

## O que muda no que já existe

Independente da direção escolhida:

1. **`0%` vira `N de M`.** "0 de 15 artigos" convida; "0%" desanima.
2. **A sidebar recua na leitura.** Hoje ela disputa com o texto o tempo todo.
3. **O "próximo passo" nasce por subtração, não por adição.** O mecanismo do roadmap.sh funciona porque o concluído é **visualmente removido** — tachado e cinza — e o que sobra em destaque é o próximo. Um checkmark verde *acrescentado* não produz o efeito: adiciona ruído em vez de limpar o caminho.

## Decisão pendente

Escolha entre **A**, **B** e **C** — ou diga o que quer de cada. A recomendação da pesquisa é **B**, pelo achado da coerência, mas a skill `visual-direction` é explícita: ela entrega opções, não elege vencedora. Depois de escolhida, construo as telas navegáveis para você comparar antes de virar código de produção.
