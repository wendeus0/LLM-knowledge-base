# ADR 0008 — Traversal de wikilinks como estratégia de enriquecimento de contexto para QA

- **Status:** Aceito
- **Data:** 2026-04-06

## Contexto

O fluxo de QA buscava artigos na wiki por contagem de palavras-chave (ADR-0004) e usava os resultados como contexto para o LLM. Esse modelo ignora o grafo implícito de wikilinks `[[conceito]]` que o compilador já gera em cada artigo, deixando relações conceituais entre artigos fora do contexto de resposta.

Para perguntas que cruzam mais de um conceito (ex: "XSS e CSP"), os artigos relevantes muitas vezes estão ligados por wikilinks mas não compartilham as mesmas palavras-chave da query.

## Decisão

Após a busca por palavras-chave, o router executa um **BFS (breadth-first search) sobre os wikilinks** dos artigos seed para enriquecer o contexto de QA. As restrições são:

1. **Token budget:** contexto total limitado a `MAX_CONTEXT_TOKENS` (padrão: 8000) — artigos são adicionados enquanto o budget permitir.
2. **Profundidade configurável:** padrão `depth=1`; expansível via `--depth N` ou `WIKILINK_TRAVERSAL_DEPTH`.
3. **Progressive disclosure:** apenas frontmatter é carregado para avaliar relevância antes de incluir o conteúdo completo.
4. **Opt-out explícito:** `--no-traverse` desativa o traversal; backward compat mantida.
5. **Deduplicação:** ciclos e artigos já incluídos no seed são ignorados.

A implementação vive em `kb/graph.py` (`extract_wikilinks`, `resolve_wikilink`, `load_frontmatter`, `traverse`).

## Consequências

### Positivas
- respostas de QA mais ricas para perguntas que cruzam conceitos relacionados
- aproveita o grafo de conhecimento já gerado pelo compilador sem custo extra de indexação
- budget de tokens garante que o contexto não exploda com profundidades maiores

### Negativas
- respostas ficam ligeiramente mais lentas (leitura extra de arquivos) para queries com muitos links
- wikilinks gerados por LLM com erros de capitalização podem não resolver (mitigado por `heal`)
- profundidades > 1 podem incluir artigos tangencialmente relacionados

## Alternativas consideradas

### A1. Embeddings + busca vetorial
- **Adiada:** captura melhor similaridade semântica, mas requer infraestrutura adicional; relevante quando a wiki escalar além de ~500 artigos (ADR-0004).

### A2. Traversal completo sem budget
- **Rejeitada:** explodiria o contexto em wikis densamente ligadas.

### A3. Manter busca apenas por palavras-chave
- **Rejeitada:** não aproveita o grafo implícito já existente na wiki.
