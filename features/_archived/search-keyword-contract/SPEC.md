---
title: Search keyword contract
epic: search
status: approved
pr:
---

# Search keyword contract

## Objetivo

Hoje a busca já funciona em `kb/search.py` e no comando `kb search`, mas sem SPEC dedicada que congele o contrato funcional e o formato de saída; esta feature formaliza esse contrato para eliminar drift e `GAP_SPEC`.

## Requisitos funcionais

- [ ] RF-01: `kb search <query>` deve pesquisar apenas arquivos `*.md` da `WIKI_DIR`, excluindo `_index.md`
- [ ] RF-02: score de relevância deve ser baseado em contagem simples de ocorrências dos termos da query (case-insensitive)
- [ ] RF-03: resultados devem ser ordenados por score decrescente e limitados por `top_k`
- [ ] RF-04: `kb.search.find_relevant(query, top_k)` deve retornar `list[Path]`
- [ ] RF-05: `kb.search.search(query, top_k)` deve retornar `list[dict]` com `path`, `score`, `snippet`
- [ ] RF-06: snippet deve ser a primeira linha do documento que contém ao menos um termo da query
- [ ] RF-07: quando não houver resultados, a camada CLI deve exibir `Nenhum resultado encontrado.` sem erro interno

## Requisitos técnicos

- RT-01: algoritmo deve permanecer determinístico e offline (sem provider externo)
- RT-02: tokenização mínima por whitespace (`query.lower().split()`), sem stemming/lemmatização nesta fase
- RT-03: implementação deve manter dependência zero de mecanismos externos de busca
- RT-04: custo computacional aceito para esta fase: varredura linear dos arquivos markdown

## Mudanças de API/CLI

- API interna:
  - `find_relevant(query: str, top_k: int = 5) -> list[Path]`
  - `search(query: str, top_k: int = 10) -> list[dict]`
- CLI:
  - `kb search <query>`
  - sem breaking change para comandos existentes

## Testes

- Unit:
  - `tests/unit/test_search.py` validando tipo de retorno, top_k, ausência de matches, estrutura de resultado
- Integration:
  - `tests/integration/test_ingest_compile_qa.py` cobrindo busca no fluxo completo
- Manual:
  1. `kb search "xss"`
  2. `kb search "termo inexistente"`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2h |
| Bloqueador | não |
| Risco | baixo |

## Dependências

- `docs/adr/0004-keyword-search-strategy.md`

## ADR

- Necessária? não
- Referência arquitetural vigente: `docs/adr/0004-keyword-search-strategy.md`

## Critérios de aceite

- [ ] `kb/search.py` e `kb/cmds/search/run.py` deixam de estar em `GAP_SPEC`
- [ ] Testes de busca passam no CI/local
- [ ] Matriz de compliance atualizada com vínculo explícito à SPEC

## Evidências esperadas

- Comandos executados:
  - `python -m pytest tests/unit/test_search.py -q`
- Arquivos alterados:
  - `features/search-keyword-contract/SPEC.md`
  - `docs/architecture/CODEBASE_SPEC_COMPLIANCE_MATRIX.md`

## Notas

Limitações conhecidas permanecem intencionais nesta versão: sem busca semântica, sem fuzzy matching e sem ranking avançado (BM25/TF-IDF completo).
