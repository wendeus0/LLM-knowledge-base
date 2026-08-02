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

**Densidade** — baixa por projeto, não por falta de conteúdo. Memória de trabalho é o recurso escasso. Critério por elemento: *isto ajuda a aprender esta coisa agora?* Se serve a outra pergunta, vai para outra tela.

**Cor** — sinal e **categoria de assunto**. A família educação usa cor para o segundo propósito, que as outras três não usam: o tópico tem cor, e ela ajuda a orientar num acervo de 1.040 artigos.

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
| **Streak diário** | Explora aversão à perda; a literatura relata culpa, ansiedade e checagem compulsiva. **O aluno que faltou por doença, prova ou falta de computador em casa perde a sequência** — o mecanismo pune exatamente a circunstância que a escola deveria absorver. O próprio Duolingo mediu que o *streak freeze* reduz churn em 21% **por aliviar ansiedade** |
| **Ranking público em turma** | Ranking entre pessoas que se veem no dia seguinte. Estudo longitudinal encontrou ausência de prática adicional e associação com **notas mais baixas**. A evidência é conflitante, não unânime — mas o risco é maior aqui porque o dono é o professor. Se houver ranking, que seja **relativo** (vizinhos de desempenho), nunca absoluto |
| **Celebração que interrompe** | Confete de 2s + redirect de 1s dá ~4,3s de espera forçada. **Quem revisa 30 cartões paga 30 vezes** — e em máquina fraca paga no frame rate também |
| **Nav por `<div>` sem `role`** | O Codédex faz isto: os controles de ícone da nav são inalcançáveis por teclado. Para alunos de escola é bloqueante |

## Acessibilidade — requisito, não polimento

Vai para escola: contraste WCAG AA no mínimo, alvo de toque adequado, foco visível, navegação por teclado em tudo, e a página precisa funcionar em máquina fraca. O `prefers-reduced-motion` do Codédex é copiável literalmente.

## O que muda no que já existe

Independente da direção escolhida:

1. **`0%` vira `N de M`.** "0 de 15 artigos" convida; "0%" desanima.
2. **A sidebar recua na leitura.** Hoje ela disputa com o texto o tempo todo.
3. **Cor por tópico** ajuda a orientar em 1.040 artigos.

## Decisão pendente

Escolha entre **A**, **B** e **C** — ou diga o que quer de cada. A recomendação da pesquisa é **B**, pelo achado da coerência, mas a skill `visual-direction` é explícita: ela entrega opções, não elege vencedora. Depois de escolhida, construo as telas navegáveis para você comparar antes de virar código de produção.
