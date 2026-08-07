# 006 — Superfície do pedido de tema

Type: prototype
Status: open
Blocked by: [o-que-e-um-tema](002-o-que-e-um-tema.md)

## Question
De onde parte o pedido de compile de tema? O ADR, decisão 6, estabelece que a plataforma de estudos tem tela própria e que v1 fecha o ciclo nela — mas não diz se o pedido de compile sai dessa tela ou de um comando de CLI. As duas superfícies implicam contratos diferentes: uma tela precisa de estado visível do pedido (pendente, compilando, pronto, stale); uma CLI precisa de saída inspecionável e de como o resultado chega à tela para a conferência renderizada que o destination exige.

A resposta depende de [o-que-e-um-tema](002-o-que-e-um-tema.md): a superfície pede "um tema", e o que se digita ou se escolhe numa lista muda completamente conforme tema seja valor de taxonomia, query livre ou entidade com slug.

## Why it matters
O destination fecha com artigo "conferido em tela renderizada", e a regra de casa exige tela renderizada para qualquer afirmação sobre tela — ou seja, a superfície faz parte do caminho de aceitação, não é detalhe de UX adiável. Sem ela definida, o PLAN da feature não sabe qual ciclo v1 fecha.

## What would settle it
Um protótipo da superfície escolhida (tela na plataforma ou fluxo CLI → tela), percorrido de ponta a ponta com um pedido de tema de mentira, mais a decisão do dono sobre qual das duas é a oficial de v1.
