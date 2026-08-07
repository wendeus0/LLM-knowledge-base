# 004 — Definir o gate "não perdeu informação"

Type: prototype
Status: open
Blocked by: [de-onde-a-sintese-le](003-de-onde-a-sintese-le.md)

## Question
O ADR trocou o gate de min-refs por "não perdeu informação" e não definiu o termo. Este ticket transforma a expressão em critério operacional: perda medida contra quê (o corpus escolhido em [de-onde-a-sintese-le](003-de-onde-a-sintese-le.md)), verificada por quem (checagem automática, conferência humana, híbrido), com qual limiar de reprovação.

A pergunta inclui o que o gate não é. Min-refs era contável; "não perdeu informação" não é obviamente contável. O ticket precisa descobrir se existe versão mensurável que o dono aceite como pass/fail — e se a reativação do min-refs, que o ADR mantém viva na decisão 1 ("artigo raso é bug"), convive com o gate novo como critério separado ou é absorvida por ele.

## Why it matters
Sem esta definição, o destination não tem critério de chegada: "conferido em tela renderizada" é mecânica de verificação, não padrão de aprovação — confere-se o quê? Também trava [destino-dos-capitulos](005-destino-dos-capitulos.md): dizer que `_chapters/` pode ser absorvido e arquivado exige saber o que significa a absorção não ter perdido nada.

## What would settle it
Uma definição escrita e testável do gate, demonstrada em pelo menos um caso real: um artigo de tema candidato (ou trecho dele) submetido ao critério, com veredito pass/fail reproduzível por terceiros. O dono aprova a definição vendo ela operar, não lendo sobre ela.
