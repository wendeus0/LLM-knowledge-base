# Síntese cruzada dos três dossiês

Type: grilling
Status: resolved
Blocked by: 001-research-hikari, 002-research-graphify, 003-research-rowboat

## Question

Onde os três repos concordam, onde divergem, e o que essa divergência diz sobre as apostas atuais do kb?

Eixos a cruzar (as cinco lentes):

- **Grafo vs plano** — Hikari e graphify materializam grafo por caminhos diferentes; o kb é plano. A convergência dos dois é evidência de quê?
- **Vetores** — graphify recusa vector store, Hikari tem `kg_vector_query.py`, rowboat sobe Qdrant. Três respostas diferentes para a mesma pergunta que o kb ainda não fez.
- **Superfície de acesso** — MCP (Hikari), skill (graphify), UI própria (rowboat), CLI+Obsidian (kb).
- **Onde o LLM entra** — determinístico onde dá, LLM onde precisa: quem traça a linha onde.

Saída: seção de síntese no diretório do map, com as tensões nomeadas — não com veredito sobre o kb.

## Answer

Documento: [SINTESE.md](../SINTESE.md).

Cinco tensões nomeadas: camada derivada vs leitura direta; curadoria manual vs automática; apagar vs tombstonar; servir como ferramenta vs responder como aplicação; prosa como ponto cego do trio.

A conclusão que reorienta o backlog: **a divergência interessante não é sobre vetores.** Os três recusam vetor como caminho principal, e o kb também — está acompanhado. A diferença é que os três mantêm uma camada derivada entre a pergunta e os arquivos (cache validado por `(mtime, size)` no Hikari, índice invertido e IDF cacheado no graphify, contexto montado no prompt no rowboat) e o kb relê o corpus inteiro a cada operação.

Correção de premissa registrada durante a síntese: a documentação do kb (`CLAUDE.md`, `AGENTS.md`) descreve a busca como "contagem simples de palavras-chave", mas `kb/search.py:59-102` implementa BM25 com IDF, densidade e fusão RRF de três canais, e `kb/graph.py:65-109` já faz travessia de wikilinks com profundidade e orçamento de tokens. O kb é mais maduro do que se documenta — e o corpus é 28× maior do que a documentação assume.
