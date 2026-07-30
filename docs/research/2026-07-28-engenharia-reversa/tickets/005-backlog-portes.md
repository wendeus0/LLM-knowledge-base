# Backlog priorizado de portes candidatos

Type: grilling
Status: resolved
Blocked by: 004-sintese-cruzada

## Question

Quais portes candidatos entram no backlog do kb, em que ordem, e qual o custo de cada um?

Cada item carrega: origem (`repo:caminho:linha`), o que o kb ganharia, custo estimado, o que teria de mudar em `SDD.md`, e se é porte de código (com atribuição de licença), de convenção ou de ideia.

Ordenação a decidir com o backlog na mão — valor para o kb ou custo de implementação (está em `Not yet specified` no map).

Este ticket fecha o map: com ele resolvido, o destination está entregue e o esforço faz ponte para `spec-pipeline` se alguma feature for eleita.

## Answer

Documento: [BACKLOG.md](../BACKLOG.md). Onze itens ordenados por valor, conforme decidido (valor, não custo nem retorno).

Topo da lista:

1. **`kb lint` audita 20 de 2.781 artigos** — não é porte, é achado. `kb/lint.py:37-39` manda `articles[:20]` ao LLM e não informa a amostragem.
2. **Índice persistente com cache por `(mtime, size)`** — o corpus inteiro é relido a cada busca, e cada wikilink dispara um `rglob` completo.
3. **Peso por campo no ranking** — título e tags valem o mesmo que palavra solta no corpo.
4. **Expansão sem filtro binário, com bloqueio de hub.**

Dois itens ficaram condicionados: dedup/merge-before-create depende de medir quantos near-duplicates existem de fato (869 fontes → 2.781 artigos); a taxonomia editorial de confiança do Hikari precisa virar check automático, porque no volume do kb nenhum gate manual sobrevive.

Registrado e não recomendado: índice autoritativo (V11). O teto de ambição acordado permitia propor mudança de premissa, e este é o único item que o faz — os três repos recusam, e um índice derivado descartável entrega o mesmo ganho sem criar segunda fonte de verdade.
