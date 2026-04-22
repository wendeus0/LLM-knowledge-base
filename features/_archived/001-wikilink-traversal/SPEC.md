---
title: Wikilink Traversal no QA
eptic: qa
status: done
---

# Wikilink Traversal no QA

## Objetivo

O router já enriquece o contexto de QA seguindo wikilinks `[[...]]` dos artigos encontrados por busca, mas faltam testes de integração para `--depth 2` e `--no-traverse`. Esta feature finaliza a integração e garante cobertura completa.

## Requisitos funcionais

- [ ] `kb qa` com `--depth 2` segue wikilinks até 2 níveis de profundidade
- [ ] `kb qa` com `--no-traverse` desativa traversal (usa apenas busca por palavra-chave)
- [ ] `kb graph.traverse` respeita budget de tokens, evita ciclos e filtra por relevância
- [ ] `kb graph.extract_wikilinks` detecta `[[link]]`, `[[Link com espaço]]`, ignora markdown normal
- [ ] `kb graph.resolve_wikilink` encontra arquivo em `wiki/**/<link>.md` (case-insensitive slug)

## Requisitos técnicos

- Reutilizar `kb/graph.py` existente (BFS sobre wikilinks)
- `kb/router.py` já integra `graph_traverse` em `_build_wiki_context`; validar pass-through de flags
- `kb/cli.py` já expõe `--depth` e `--no-traverse`; validar wiring até `execute_qa_command`

## Mudanças de API/CLI

Nenhuma breaking change. Flags já existentes:

- `--depth INT` (padrão: 1)
- `--no-traverse` (padrão: ativado)

## Testes

- Unit: `test_graph.py` — extrair links, resolver paths, frontmatter, budget, ciclos, depth, relevância
- Integration: `test_router.py` — `build_context` com `traverse=False` e `depth=2`
- Integration: `test_qa_command.py` — end-to-end de `execute_qa_command` com flags

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 2-3h  |
| Bloqueador | não   |
| Risk       | baixa |

## Dependências

- `graph.py` implementado
- `router.py` com integração base
- `cli.py` com flags expostas

## Notas

- Código de produção já está implementado; foco desta feature é cobertura de testes e remoção de comentários stale
