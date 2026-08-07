# 003 — De onde a síntese lê

Type: grilling
Status: open
Blocked by: nada

## Question
Quando o usuário pede um tema, a síntese lê o quê? O candidato interno são os 630 capítulos já compilados em `wiki/_chapters/`: em português, limpos, curados — mas inalcançáveis por qualquer retrieval hoje, porque a convenção `_*` os exclui de busca, embeddings, índice lexical e grafo (E2). O candidato externo são as fontes brutas de `raw/` + `library/`: 800 capítulos .md mais 23 binários PDF/EPUB ainda não extraídos, com `library/` lida apenas para proveniência e classificação de ruído, nunca como corpus (E5, E6).

Os dois caminhos carregam dívidas diferentes. Ler de `_chapters/` exige tornar essa camada recuperável, ao menos para a síntese. Ler das fontes brutas exige retrieval sobre `library/` que o ADR declarou pré-requisito e que não existe (E6), além de decidir o que fazer com os 23 binários e com o fato de que só 34 dos 43 livros de `software-engineering/` têm `metadata.json` (E5).

## Why it matters
É a decisão de corpus da feature inteira. O gate de "não perdeu informação" ([gate-nao-perdeu-informacao](004-gate-nao-perdeu-informacao.md)) não pode ser definido sem saber contra qual texto a perda é medida. A modelagem de estado 1:N ([estado-1-para-n](007-estado-1-para-n.md)) depende de saber o que conta como fonte registrável. E o destino de `_chapters/` ([destino-dos-capitulos](005-destino-dos-capitulos.md)) muda completamente conforme essa camada seja insumo da síntese ou subproduto aposentável.

## What would settle it
Uma decisão do dono sobre o corpus de leitura da síntese, com a consequência explícita para a camada não escolhida: se `_chapters/` não é lida, o que ela vira; se `library/` não é lida, o pré-requisito do ADR é formalmente revogado ou adiado.
