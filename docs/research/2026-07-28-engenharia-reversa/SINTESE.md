# Síntese cruzada — rowboat, graphify, Hikari-knowledge

Resolve o ticket [Síntese cruzada dos três dossiês](tickets/004-sintese-cruzada.md). Cada afirmação sobre os repos externos tem evidência nos dossiês irmãos; cada afirmação sobre o kb tem evidência em `kb/*.py` deste repositório.

## 1. A convergência: arquivo é a verdade

Três equipes independentes, três recusas a fazer do índice a fonte da verdade.

| | Fonte autoritativa | Camada derivada | Vetores |
|---|---|---|---|
| Hikari | Markdown em `nodes/` | `graph.json`, que o servidor MCP nem lê | Opcional, **desligado por padrão** |
| graphify | Código e documentos originais | Grafo NetworkX derivado por AST | **Nenhum**, em ponto algum |
| rowboat | Markdown em `Agent Notes/` | Contexto montado no prompt | Só RAG de documentos, sistema separado |
| **kb** | **Markdown em `wiki/`** | **nenhuma** | nenhum |

A aposta do kb sai validada por convergência. O contraste é a última coluna da terceira linha: os três têm uma camada derivada sobre os arquivos, e o kb não tem. Ele consulta o texto bruto diretamente, a cada pergunta.

## 2. A divergência: onde o vetor entra

A pergunta que o kb nunca formulou recebeu três respostas diferentes:

- **graphify recusa**: sem vector store, e sem match ele responde `No matching nodes found.` e para. Não degrada para semântico.
- **Hikari admite como bônus**: `KG_VECTOR` desligado por padrão; quando ligado, entra por reciprocal-rank fusion `300/(10+rank)`, calibrado para nunca deslocar um hit lexical exato (id integral vale ~1000, teto do bônus vetorial ~30).
- **rowboat separa**: Qdrant existe, mas para RAG de documentos de projeto, filtrado por `projectId`/`sourceId`. A memória pessoal do agente não passa por lá.

Nenhum dos três usa vetor como caminho principal de recuperação. O kb, que também não usa, está acompanhado — mas por motivos que os outros três explicitaram e ele não.

## 3. A tensão real não é vetor: é ausência de camada derivada

O kb já faz mais do que sua própria documentação declara. `CLAUDE.md` diz "TF-IDF simples + busca de palavra-chave"; o código faz BM25 com IDF, densidade e fusão RRF de três canais (`kb/search.py:59-102`), e traversal de wikilinks com BFS, profundidade e orçamento de tokens (`kb/graph.py:65-109`). Há ainda lifecycle de claims com decay e checagem de contradição (`kb/claims.py:141-232`), arquivamento por órfão/idade/staleness (`kb/archive.py:32-119`) e sumário de saúde com thresholds (`kb/analytics/health.py:16-70`).

O que os três repos têm e o kb não é **estado materializado entre a pergunta e os arquivos**:

- Hikari cacheia por `(mtime, size)` e resolve id→path por dicionário.
- graphify mantém índice invertido de trigramas e IDF cacheado no objeto do grafo.
- O kb relê os 2.781 arquivos (36 MB) a cada busca (`kb/search.py:24-31`) e, pior, resolve **cada** wikilink com um `rglob("*.md")` sobre o diretório inteiro (`kb/graph.py:17-23`) — chamado uma vez por link durante a travessia (`kb/graph.py:89`).

Na escala de 47 nós do Hikari, isso é irrelevante. Na escala de 2.781 artigos do vault real, é o gargalo.

## 4. Escala: os três operam em faixas diferentes, e o kb está na maior

| | Corpus | Régua |
|---|---|---|
| Hikari | 47 nós | Curadoria manual por evento de julgamento é viável |
| graphify | Testado até ~1M LOC | Avisa: >500K palavras ou >500 arquivos, extração semântica fica cara |
| **kb (vault real)** | **2.781 artigos, 4.26M palavras** | 59× o Hikari; 8× o limite de alerta do graphify |

Consequência que atravessa todo o backlog: **gates de curadoria manuais não portam.** O Hikari decide nota a nota porque tem 47. Qualquer gate no kb precisa ser check automático, ou vira gargalo humano.

## 5. Onde cada um traça a linha do determinismo

Todos separam o que é mecânico do que precisa de modelo, mas em pontos diferentes:

- **graphify**: AST determinístico para código; LLM só para documentos, papers e imagens. Retrieval é 100% determinístico. Prosa, portanto, é cidadã de segunda classe — o extrator de markdown pega headings e links, nada mais.
- **Hikari**: tudo determinístico exceto o embedding opcional. Curadoria é o humano com o agente, sob gates escritos.
- **rowboat**: a decisão de reter é do LLM, sob instrução; a recuperação é carregamento de arquivo, sem busca.
- **kb**: retrieval determinístico (BM25/RRF); compile, heal e lint são LLM.

Aqui o kb tem um problema específico que nenhum dos três tem: **`kb lint` manda para o LLM apenas os 20 primeiros artigos** que o `rglob` devolver (`kb/lint.py:37-39`), sobre um corpus de 2.781. A detecção de wikilink quebrado varre tudo (`kb/lint.py:29-35`), mas a auditoria semântica vê 0,7% do corpus e não diz isso a quem roda. Hikari roda `build_graph.py --check` sobre o corpus inteiro; graphify constrói sobre tudo.

## 6. Superfície de acesso

- **Hikari**: MCP local por stdio, quatro ferramentas (`kg_search`, `kg_get`, `kg_neighbors`, `kg_index`). Nenhuma gera prosa — devolvem ranking, markdown bruto, subgrafo, índice. Toda geração fica no cliente.
- **graphify**: instala-se como skill em Claude Code, Codex, Cursor, Gemini CLI, gerada deterministicamente de fragmentos.
- **rowboat**: UI própria que expõe estado operacional — topologia de agentes em Mermaid, ciclo de vida de jobs, draft/live, reasoning e tool calls como itens tipados. Streaming por SSE.
- **kb**: CLI + Obsidian sobre `wiki/`.

O padrão dos três primeiros: **a base de conhecimento é servida como ferramenta, não como aplicação.** O cliente LLM traz a geração. O kb faz o oposto — `kb qa` chama o modelo por dentro (`kb/qa.py:80-94`). Não é erro, é uma escolha diferente, e ela é a razão pela qual o Obsidian sozinho não dá acesso ao corpus para um agente externo.

## 7. Tensões nomeadas

1. **Camada derivada vs leitura direta.** Os três materializam algo; o kb relê tudo. Em 2.781 artigos isso já custa.
2. **Curadoria manual vs automática.** O Hikari oferece os melhores gates editoriais do trio, e são exatamente os que não escalam para o volume do kb sem virar check de máquina.
3. **Apagar vs tombstonar.** `heal` do kb faz `path.unlink()` em stub (`kb/heal.py:65`); Hikari nunca apaga, converte em tombstone com `superseded_by`. O kb tem `archive.py`, que move em vez de apagar — duas políticas convivendo no mesmo produto.
4. **Servir como ferramenta vs responder como aplicação.** MCP/skill nos três; `kb qa` monolítico aqui.
5. **Prosa é o ponto cego do trio.** graphify trata prosa como segunda classe, Hikari cura à mão em escala pequena, rowboat guarda notas curtas. Nenhum resolve "4 milhões de palavras de prosa" — que é exatamente o caso do kb. **Não há porte pronto para o problema central; há mecanismos a adaptar.**
