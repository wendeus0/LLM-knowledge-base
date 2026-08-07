# 008 — Qualidade da proveniência do manifest

Type: research
Status: open
Blocked by: nada

## Question
Qual é a taxa de erro da proveniência do manifest? 824 de 856 entradas (96%) foram atribuídas por `backfill-basename` — match de nome de arquivo entre `library/` e wiki — com apenas 19 por conteúdo e 13 por cosseno (E4). A cadeia de desempate (`kb/backfill.py:81-115`) tenta basename primeiro, e o que não desempata vira `unresolved`. A pergunta é empírica: em que proporção o match por nome de arquivo aponta para o livro errado?

O ADR faz da proveniência O critério de agrupamento de fontes em temas. Se o basename erra em taxa relevante — nomes genéricos, edições diferentes, capítulos homônimos entre livros — então uma fatia dos 856 vínculos fonte↔artigo está errada, e qualquer agrupamento construído sobre eles herda o erro.

Há um segundo eixo de erro, mais barato de medir e já visível: o **falso negativo**. Sete artigos ficaram soltos na raiz da wiki, sem diretório de topic, com títulos que os denunciam como capítulos de livro — *API Design Patterns* front matter, "dentro da capa: tópicos de design de APIs", `honeycomb.md` (*Observability Engineering*), "introdução à integração de aplicações com mensageria" (*Enterprise Integration Patterns*) — e continuam na wiki apenas porque o backfill não conseguiu pareá-los (E13). Eles são amostra pronta: para cada um, a fonte existe em `library/` ou `_sources/` e não foi encontrada. Entender por que falharam dá a taxa de falso negativo sem construir amostragem nenhuma.

## Why it matters
Este ticket pode derrubar [medir-sobreposicao-tematica](001-medir-sobreposicao-tematica.md), e por isso o bloqueia: se a proveniência é ruidosa, medir sobreposição sobre vínculos errados produz um ranking de pilotos inválido e um número de gatilho incorreto para [destino-dos-capitulos](005-destino-dos-capitulos.md). A assimetria é desfavorável — o custo de medir a taxa de erro é pequeno; o custo de construir o piloto sobre proveniência podre é o destination inteiro.

## What would settle it
Uma medição (AFK) das duas taxas de erro, separadas:

1. **Falso positivo** — amostra das 824 atribuições por basename, verificada contra os sinais mais fortes disponíveis (conteúdo normalizado, cosseno), com taxa estimada e intervalo de confiança.
2. **Falso negativo** — diagnóstico dos 120 `unresolved`, começando pelos 7 soltos na raiz da wiki, que têm fonte identificável a olho: por que a cadeia falhou em cada um (basename divergente, fonte só em binário, capítulo homônimo, ausência de `metadata.json`).

E um veredito explícito: basename é confiável o suficiente para alimentar o agrupamento de temas, sim ou não — e, se não, qual o tamanho e a localização do estrago.
