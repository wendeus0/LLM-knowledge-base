# 005 — Destino de `_chapters/` depois que o tema nasce

Type: grilling
Status: open
Blocked by: [medir-sobreposicao-tematica](001-medir-sobreposicao-tematica.md), [gate-nao-perdeu-informacao](004-gate-nao-perdeu-informacao.md)

## Question
Depois que o primeiro artigo de tema existir, o que acontece com `wiki/_chapters/`? As alternativas que o ADR colocou na mesa são: camada transitória — absorvida pelos artigos de tema e arquivável — ou camada permanente, que continua a existir como insumo recuperável ao lado dos temas.

O ADR já registrou o gatilho de revisão: se a medição mostrar que capítulo alimenta vários temas com frequência, `_chapters/` vira permanente. Ou seja, a decisão tem uma dependência numérica explícita em [medir-sobreposicao-tematica](001-medir-sobreposicao-tematica.md) — e uma dependência lógica em [gate-nao-perdeu-informacao](004-gate-nao-perdeu-informacao.md), porque "absorvido" só é uma palavra honesta se houver critério para afirmar que nada se perdeu na absorção.

## Why it matters
O destino desta camada decide se a convenção `_*` (E2) permanece como arquitetura ou vira dívida: uma camada permanente que nenhum retrieval alcança é um corpo de 630 documentos mortos por construção. Também decide o tamanho do trabalho futuro — arquivar é um lote destrutivo (com tag, relatório e aprovação, pelas regras de casa); tornar permanente e recuperável é mudança de infraestrutura.

## What would settle it
Uma decisão do dono, tomada com o número de sobreposição em mãos e o gate definido: transitório ou permanente, e no caso escolhido, a primeira consequência concreta (o plano de arquivamento ou a exigência de recuperabilidade).
