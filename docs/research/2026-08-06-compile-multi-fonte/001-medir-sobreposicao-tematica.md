# 001 — Medir sobreposição temática dos capítulos

Type: research
Status: open
Blocked by: [qualidade-da-proveniencia](008-qualidade-da-proveniencia.md)

## Question
Quantos dos 630 capítulos de `wiki/_chapters/` alimentariam MAIS DE UM tema, e qual tema tem o conjunto de fontes mais limpo para ser o piloto? A pergunta tem duas metades inseparáveis: a distribuição de sobreposição (quantos capítulos caem em dois, três, N temas candidatos) e o ranking de temas por qualidade de fontes (tamanho do conjunto, proveniência confiável, ausência de binários e de `unresolved`).

A dificuldade é real e medida: `_chapters/` está fora do índice de embeddings e de todo retrieval (E2), então não existe sinal pronto para esta medição — ela exige passe próprio sobre os 630 capítulos. Agravante de modelagem: o frontmatter de capítulo não tem `book` (E9); o livro é o diretório-pai, e qualquer agrupamento por fonte precisa reconstruir essa relação.

## Why it matters
É a pendência que o ADR deixou explícita e é também o gatilho de revisão de `_chapters/`: se capítulo alimenta vários temas com frequência, `_chapters/` deixa de ser transitório e vira camada permanente — decisão que o ticket [destino-dos-capitulos](005-destino-dos-capitulos.md) não pode tomar sem este número. O dono já decidiu que o tema piloto sai desta medição, não de preferência. E a experiência anterior mostra que a janela de clustering é estreita e instável (E12: limiar 0,88 dá 116 grupos; em 0,85 o maior grupo salta de 31 para 148), então a medição precisa reportar sensibilidade, não um número único.

## What would settle it
Uma medição executada e registrada (AFK), contendo: a distribuição capítulo × quantidade de temas candidatos sobre os 630 capítulos; a sensibilidade dessa distribuição ao limiar/método escolhido; e um ranking de temas candidatos a piloto com, para cada um, o conjunto de fontes, o tamanho em capítulos e as ressalvas de qualidade (binários, `unresolved`, proveniência por basename). O artefato fecha o ticket se permite ao dono apontar o piloto sem nova rodada de exploração.
