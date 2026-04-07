# ADR 0004: Estratégia de Busca por Keywords Simples

**Status:** Aceito  
**Data:** 2026-04-04  
**Autor:** Sistema kb

---

## Contexto

O sistema kb é uma engine de knowledge base mantida por LLM que precisa fornecer capacidade de busca sobre a wiki em Markdown. A wiki pode crescer para milhares de arquivos no corpus do usuário, mas ainda não se trata de um sistema de produção com milhões de documentos.

A necessidade é permitir que usuários encontrem documentos relevantes através de termos de busca, sem adicionar complexidade de infraestrutura externa ao projeto.

## Decisão

Adotar busca por **contagem simples de palavras-chave** em arquivos Markdown, implementada em Python puro sem dependências externas de busca.

A estratégia funciona assim:

1. Extrair todas as palavras dos arquivos Markdown (conteúdo + frontmatter)
2. Para cada termo de busca, contar ocorrências em cada documento
3. Ordenar resultados por frequência de ocorrência
4. Retornar os N documentos com maior score

## Consequências

### Positivas

- **Zero dependências externas**: Não requer SQLite FTS, Elasticsearch, ou serviços de vector search
- **Funciona offline**: Sem necessidade de conectividade para APIs de embeddings
- **Rápido para corpus locais de usuário**: Escala bem para milhares de documentos em hardware modesto
- **Código simples**: Fácil de entender, manter e depurar
- **Sem configuração**: Não requer setup de índices, schemas ou tuning
- **Determinístico**: Mesma busca sempre retorna mesmos resultados

### Negativas

- **Precisão limitada**: Não entende sinônimos, variações de palavras ou contexto semântico
- **Sem busca por similaridade**: "car" não encontra "automobile"
- **Performance O(n)**: Escaneia todos os arquivos a cada busca (aceitável para milhares, não para milhões)
- **Sem ranking semântico**: Documentos relevantes semanticamente mas sem palavras exatas não são encontrados
- **Limitado a termos exatos**: Não faz stemming ou lemmatização automaticamente

## Alternativas Consideradas

| Alternativa                    | Por que não foi escolhida                                                                                              |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **SQLite FTS**                 | Adiciona dependência de banco de dados, requer schema e migrações, complexidade desnecessária para corpus local        |
| **Elasticsearch**              | Infraestrutura pesada, requer servidor dedicado, overkill para o escopo atual                                          |
| **Vector search / Embeddings** | Requer API de LLM para gerar embeddings, custo adicional, latência de rede, não funciona totalmente offline            |
| **ripgrep (rg)**               | Excelente performance, mas é uma ferramenta externa; preferimos solução puramente Python para portabilidade e controle |
| **Whoosh (Python FTS)**        | Biblioteca dedicada de full-text search, mas adiciona dependência pesada; nossa solução simples é suficiente           |

## Quando Reconsiderar

Esta decisão deve ser revisitada se:

1. **Escala aumentar significativamente**: Wiki crescer além de ~10.000 documentos onde scan O(n) se torna perceptivelmente lento
2. **Necessidade de busca semântica**: Usuários precisarem encontrar documentos por conceito/conceitos relacionados, não apenas palavras exatas
3. **Necessidade de relevância avançada**: Requisitos de ranking por TF-IDF, BM25, ou outros algoritmos de relevância
4. **Busca fuzzy**: Necessidade de tolerância a typos ou variações ortográficas
5. **Query complexa**: Suporte a operadores booleanos (AND, OR, NOT), wildcards, ou frases exatas com alta performance

## Implementação

A implementação atual está em `kb/search.py` e realiza:

```python
# Pseudocódigo da estratégia
def search(query, wiki_dir):
    terms = tokenize(query.lower())
    scores = {}

    for md_file in list_markdown(wiki_dir):
        content = read(md_file).lower()
        score = sum(content.count(term) for term in terms)
        if score > 0:
            scores[md_file] = score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

## Referências

- `kb/search.py`: Implementação atual
- ADR 0001: Arquitetura geral do kb
- [Pawel Huryn - Knowledge Management System](https://pawelhuryn.com/knowledge-management-system/): Inspiração para estratégia de automação LLM
