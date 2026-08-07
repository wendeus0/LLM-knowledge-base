# 007 — Estado: de 1 fonte para N fontes por artigo

Type: research
Status: open
Blocked by: [de-onde-a-sintese-le](003-de-onde-a-sintese-le.md)

## Question
Como manifest e knowledge modelam um artigo sintetizado de N fontes? Hoje o estado é 1:1 por construção, não por acidente: 856 entradas, 856 artigos distintos, zero artigos multi-fonte (E3). `mark_compiled` grava uma fonte por entrada (`kb/state.py:88-108`) e `upsert_knowledge` chaveia por fonte (`kb/state.py:232-258`) — a unicidade de fonte está escrita nas duas primitivas que o compile usa.

A pergunta cobre o desenho todo: qual é a chave de um artigo de tema (o tema? um slug? a lista de fontes?), como as N fontes são registradas sem quebrar o que já existe, e o que acontece com o fingerprint, cuja varredura da wiki inteira (`kb/api/articles.py:39-49`, a única exceção à convenção `_*`, E2) assume um certo formato de estado. O que conta como "fonte" depende de [de-onde-a-sintese-le](003-de-onde-a-sintese-le.md): capítulo compilado e arquivo bruto têm identidades diferentes.

## Why it matters
É a mudança de invariante central do sistema de estado: de "uma fonte por artigo" para "N fontes por artigo". Mexer nisso sem levantamento é como toda a proveniência, o backfill e a detecção de já-compilado se comportam — e o manifest de 856 entradas não pode ser invalidado pela migração.

## What would settle it
Um levantamento (AFK) das estruturas atuais e dos pontos de impacto, com as alternativas de modelagem 1:N descritas contra o código real: chave, registro de fontes, efeito no fingerprint e no backfill, e compatibilidade com as 856 entradas existentes. O ticket fecha quando o dono consegue escolher uma alternativa sem nova rodada de leitura de código.
