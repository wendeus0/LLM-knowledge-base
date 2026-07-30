# Engenharia reversa — graphify

Type: research
Status: resolved
Blocked by: —

## Question

Como o `Graphify-Labs/graphify` transforma corpus heterogêneo (código, docs, SQL, PDF) em grafo consultável sem vector store, e o que disso serve ao retrieval e ao modelo de dados do kb?

Alvo do dossiê:

1. **Modelo do grafo** — o que é nó e aresta, onde o grafo é persistido, formato, custo de rebuild. Ler `ARCHITECTURE.md` e o pacote `graphify/`.
2. **Extração determinística** — como o AST parsing produz arestas sem LLM, e onde (se em algum lugar) o LLM ainda entra. A promessa "every edge explained" é verificável no código?
3. **Retrieval sem vetores** — como uma pergunta vira consulta ao grafo. Este é o eixo mais valioso: o kb aposta em keyword simples e precisa saber o que existe entre isso e RAG.
4. **Escala** — `BENCHMARKS.md`: números reais de corpus, tempo e memória; onde a abordagem quebra.
5. **Corpus não-código** — como docs/PDF entram no mesmo grafo que código. O kb é corpus de prosa, então esta é a parte que mais se aplica.
6. **Entrega como skill** — `tools/skillgen/`: como empacotam a capacidade para Claude Code/Codex.

## Answer

Dossiê: [DOSSIE-graphify.md](../DOSSIE-graphify.md). Commit lido `0b2bd93`, pacote `graphifyy` 0.9.29. Executado por GPT 5.6 Terra (effort high) via `fable-gpt`; review zero-trust aprovado, zero caminhos citados inexistentes.

Gist — o eixo mais valioso é o retrieval, e ele é descrito até o mecanismo:

- **Recuperação é léxico + travessia de grafo, sem vetor em nenhum ponto.** Pergunta → tokens (stopwords em 6 idiomas) → peso IDF `log(1+N/(1+df))` → casamento contra label, label tokenizado, id do nó e `source_file` → ranking com bônus fixos (igualdade 1000, prefixo 100, substring 1, caminho-fonte 0,5) multiplicados por IDF.
- **No máximo 3 sementes**, cortando abaixo de 20% do score da primeira, mais uma semente garantida por termo — defesa contra um identificador exato incidental engolir os outros termos da pergunta.
- **Expansão BFS/DFS com bloqueio de hub:** nó no percentil 99 de grau (piso 50) não serve de trânsito, só de semente. É o que impede explosão combinatória sem precisar de ranking semântico.
- **Sem match, sem resposta:** retorna literalmente `No matching nodes found.` Não há fallback semântico nem geração. O grafo responde ou cala.
- **Saída é subgrafo textual com proveniência por linha:** cada aresta carrega relação, confiança e a linha onde a relação ocorre; corte por orçamento de tokens (~`budget*3` chars) com truncamento anunciado. É isso que sustenta o "every edge explained".
- **Confiança em três níveis:** `EXTRACTED` 1.0 (sintaxe explícita), `INFERRED` 0.5 (resolução entre arquivos), `AMBIGUOUS` 0.2. Colisão de alias em import deixa o alvo pendente em vez de fabricar aresta.
- **Prosa é cidadã de segunda classe.** Markdown tem extrator determinístico, mas só de headings e links (`contains`, `references`); a extração conceitual rica de documentos/PDF depende de LLM. Como o corpus do kb é prosa, este é o achado que mais restringe o porte.
- **Salvaguardas de LLM dignas de nota:** conteúdo encapsulado como `untrusted_source`, sentinelas de prompt injection neutralizados por zero-width space (preservando offsets), e símbolo `code` alucinado pelo modelo é rebaixado a `verification: unverified` em vez de descartado.
- **Números publicados** (alegação do repo, não reproduzida): LOCOMO recall@10 0,497; LongMemEval-S QA 76%; ERPNext ~1M LOC com 82,0% de cobertura contra 70,8% de grep/read.
- Avisa abaixo de 50 mil palavras que talvez nem valha grafo — faixa em que o kb ainda está.
