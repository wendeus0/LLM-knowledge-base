# 002 — O que é um tema

Type: grilling
Status: open
Blocked by: nada

## Question
O que é, formalmente, um "tema" neste vault? Três candidatos estão sobre a mesa e são mutuamente incompatíveis como definição: um valor da taxonomia fechada de 10 `topics`; uma query livre que o usuário digita quando pede; ou uma entidade própria, com slug estável e versionável, que existe no vault independentemente de como foi pedida.

A escolha contamina tudo a jusante. Se tema é valor da taxonomia, a síntese herda os limites dela. Se é query livre, dois pedidos sobre o mesmo assunto podem gerar dois artigos. Se é entidade com slug, alguém precisa decidir quem cria slugs, como se resolve duplicidade e o que significa versionar um tema.

## Why it matters
A taxonomia atual é degenerada como candidata: dos 345 artigos vivos, 214 estão em `algorithms` e 89 em `learning` — 303 de 345 em dois valores — enquanto arquitetura, Python e testes nem aparecem porque estão todos em `_chapters/` (E7). Uma taxonomia nesse estado não serve como espaço de temas sem redefinição, e o ADR não redefiniu. Enquanto esta questão não fecha, [superficie-do-pedido](006-superficie-do-pedido.md) não sabe o que a tela pede, e nenhum gate consegue dizer sobre o quê incide.

## What would settle it
Uma decisão do dono, registrada em prosa: a definição de tema, sua identidade (slug ou não), sua relação com os 10 `topics` atuais e o que acontece quando dois pedidos apontam para o mesmo assunto.
