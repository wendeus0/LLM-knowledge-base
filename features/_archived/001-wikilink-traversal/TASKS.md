# TASKS — Wikilink Traversal no QA

| ID  | Descrição                                                                        | Status | Depende de |
| --- | -------------------------------------------------------------------------------- | ------ | ---------- |
| T1  | Criar SPEC, PLAN, TASKS                                                          | done   | —          |
| T2  | Remover comentários "RED" stale de `test_graph.py`                               | done   | T1         |
| T3  | Adicionar teste `test_should_follow_depth_2` em `test_graph.py`                  | done   | T1         |
| T4  | Adicionar testes de integração em `test_router.py` (`traverse=False`, `depth=2`) | done   | T1         |
| T5  | Adicionar teste end-to-end de `execute_qa_command` com flags                     | done   | T1         |
| T6  | Rodar quality-gate (pytest + coverage)                                           | done   | T2-T5      |
