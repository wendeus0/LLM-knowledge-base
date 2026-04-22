# PLAN — Wikilink Traversal no QA

## Arquitetura

```
kb qa "pergunta" --depth 2
  → cli.py: parse flags
  → cmds/qa/run.py: execute_qa_command(traverse=True, depth=2)
  → qa.py: answer(traverse=True, depth=2)
  → router.py: build_context(traverse=True, depth=2)
    → _build_wiki_context()
      → search.find_relevant() → seed_files
      → graph.traverse(seed_files, depth=2) → extra_files
      → concatena e lê conteúdo
```

## Decisões

1. **Sem alterar `graph.py`**: implementação BFS existente atende aos requisitos.
2. **Sem alterar `router.py`**: wiring já correto; apenas adicionar testes de integração.
3. **Remover comentários "RED" de `test_graph.py`**: código já está implementado e testes passam.

## Arquivos a modificar

- `tests/unit/test_graph.py` — remover comentários stale
- `tests/unit/test_router.py` — adicionar testes de `traverse=False` e `depth=2`
- `tests/integration/test_qa_command.py` — adicionar teste end-to-end

## Gate de qualidade

- Todos os testes existentes continuam passando
- Novos testes passam
- Cobertura de `graph.py` e `router.py` mantida ≥ 90%
