# Map — o kb como ferramenta de estudo

**Aberto:** 2026-08-01
**Dor declarada pelo usuário:** "Estou há dois dias tentando tornar essa ferramenta útil para um estudo de hacking e cibersegurança. Até agora só tentamos corrigi-la, não saímos daqui."

## Enquadramento

Este map **não** é sobre corrigir defeitos — esse trabalho tem seu próprio backlog. É sobre a distância entre "a engine funciona" e "eu uso isto para estudar". São coisas diferentes, e a sessão de 2026-08-01 mostrou que a primeira estava sendo confundida com a segunda.

Escopo definido pelo usuário: o caminho até o estudo (o que falta) **e** a qualidade do que o kb produz. Fora de escopo: reagrupamento do corpus de engenharia de software (ticket 006 do map anterior — bloqueado por pré-requisito e ortogonal a este objetivo).

## O que já é fato, medido nesta sessão

| Fato | Evidência |
|---|---|
| A geração deixou de ser o gargalo | Codex `gpt-5.6-luna` via shim em `:1236`: `kb qa` em 45s, `compile` de 5 artigos em 39s. Antes: 3 timeouts de 3 tentativas com o bonsai local |
| O rerank continua sendo gargalo | `bonsai-27b-1bit` em `:8081` é o único caminho que ainda exige `--no-rerank` |
| O corpus não é sobre o tema de estudo | ~40 livros de engenharia de software fatiados em capítulos; 15 artigos de cibersegurança |
| A verificação de ancoragem funciona em produção | Primeira pergunta real trouxe vereditos `ancorada` com evidência |
| O material bruto de segurança estava parado | GHDB e Google Hacking estavam em `raw/` sem compilar desde antes desta sessão |

## Tickets

| # | Pergunta | Estado |
|---|---|---|
| 001 | Qual é a interface de consumo, e de qual projeto OSS ela parte? | aberto |
| 002 | De onde vem o material de estudo, e com que cadência? | aberto |
| 003 | O artigo compilado presta para estudar? Qual o gate de qualidade que falta? | aberto |
| 004 | O rerank fica, sai ou troca de modelo? | aberto |
| 005 | Os 1.037 artigos de engenharia atrapalham o estudo de segurança? | aberto |

## Regra deste map

Nenhum ticket vira execução antes de ter `## Answer` preenchido. A sessão que originou este map fechou por eu tratar uma dor como ordem de serviço e ir produzir artigo sem decidir nada — o erro que este documento existe para não repetir.
