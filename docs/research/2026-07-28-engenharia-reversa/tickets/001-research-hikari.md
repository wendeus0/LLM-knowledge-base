# Engenharia reversa — Hikari-knowledge

Type: research
Status: resolved
Blocked by: —

## Question

Como o `hikarioyama/Hikari-knowledge` resolve o mesmo problema do kb — corpus markdown curado por LLM, servido ao Obsidian — e o que dele é portável?

Alvo do dossiê, nesta ordem de prioridade:

1. **Método de curadoria** — o que faz uma nota ser "measured": formato, frontmatter, granularidade, critério de entrada, defesa contra nota-lixo. Ler `docs/CONVENTIONS.md`, `docs/DECISIONS.md`, `skills/hikari-knowledge-curate/`.
2. **Grafo** — `graph.json` e `tools/build_graph.py`: o que é nó, o que é aresta, se o grafo é derivado ou autoritativo, como se mantém em sincronia com as notas.
3. **Acesso via MCP** — `mcp/server.py`, `kg_core.py`, `kg_vector_query.py`: quais ferramentas expõe, se há vetores de verdade e quando entram, como o grafo e o texto se combinam na resposta.
4. **Tooling do corpus** — `tools/obsidianize.py`, `tools/sync_vault.sh`: o que é automatizado para manter o vault vivo; comparável a `heal`/`lint`/`jobs` do kb.
5. **Skills** — `skills/hikari-knowledge*`: como o agente é instruído a operar sobre o corpus.

## Answer

Dossiê: [DOSSIE-hikari-knowledge.md](../DOSSIE-hikari-knowledge.md). Commit lido `3a67844`. Executado por GPT 5.6 Terra (effort high) via `fable-gpt`; review zero-trust aprovado com quatro âncoras amostradas contra o código.

Gist:

- **Markdown é autoritativo, `graph.json` é projeção** (`tools/build_graph.py:1-9`). O MCP nem lê o grafo serializado — relê `nodes/**/*.md` a cada request, com cache por `(mtime, size)`. Mesma premissa do kb, com grafo derivado por cima em vez de no lugar.
- **Duas arestas apenas:** `link` (de `links:` e de wikilinks `[[id]]` no corpo) e `superseded_by`. 47 nós, 157 arestas na revisão lida.
- **Retrieval é lexical primeiro, vetor é bônus opcional desligado por padrão** (`KG_VECTOR=0`). Quando ligado, entra por reciprocal-rank fusion `300/(10+rank)` — calibrado para nunca deslocar hit lexical exato (id integral vale ~1000, bônus vetorial máximo ~30). É a resposta mais direta à pergunta que o kb não fez.
- **Curadoria por evento de julgamento, não por crawling.** Gates duros antes de criar nó: merge-before-create, números só com condições (`n` e setup), `confidence` em `measured|reported|mixed`, fontes públicas, proibição de diário e de número solto. Conteúdo derrubado vira tombstone, nunca é apagado.
- **`related:` é espelho gerado de `links:`** para o Obsidian ler graph view e backlinks — uma relação editorial, uma projeção, geração idempotente.
- **Quatro ferramentas MCP:** `kg_search`, `kg_get`, `kg_neighbors`, `kg_index`. Nenhuma gera prosa: devolvem ranking, markdown bruto, subgrafo ou índice. O LLM fica do lado do cliente.
- Curiosidade operacional: o tooling emite mensagens em japonês, apesar do corpus ser publicado em inglês.
