# TDD.md

Convenções de teste para kb.

## Framework

pytest + fixtures

## Localização

```
tests/
├── unit/
│   ├── test_compile.py
│   ├── test_qa.py
│   ├── test_search.py
│   ├── test_heal.py
│   └── test_lint.py
├── integration/
│   ├── test_ingest_compile_qa.py
│   ├── test_file_back.py
│   └── test_heal_workflow.py
├── fixtures/
│   ├── raw/          ← documentos de teste
│   └── wiki/         ← wiki pré-compilada de teste
└── conftest.py       ← fixtures compartilhadas
```

## Convenções

### Unit tests

**Arquivo:** `test_<modulo>.py`

**Padrão:** Cada função pública merece um teste

```python
def test_compile_file_creates_wiki_article(tmp_path):
    # Arrange
    raw_dir = tmp_path / "raw"
    wiki_dir = tmp_path / "wiki"
    raw_file = raw_dir / "test.md"
    raw_file.write_text("# Teste\nConteúdo sobre XSS")

    # Act
    result = compile_file(raw_file)

    # Assert
    assert result.exists()
    assert result.parent.name in ["cybersecurity", "ai", "python", "typescript"]
```

### Integration tests

**Arquivo:** `integration/test_<workflow>.py`

**Padrão:** Full pipeline (raw → wiki → qa)

```python
def test_ingest_compile_qa_workflow(tmp_path):
    # Setup
    raw_dir = tmp_path / "raw"
    wiki_dir = tmp_path / "wiki"

    # Ingest
    raw_file = raw_dir / "article.md"
    raw_file.write_text("...")

    # Compile
    compile_file(raw_file)

    # QA
    response = answer("what is mentioned?")
    assert len(response) > 10
```

## Fixtures

**conftest.py:**

```python
import pytest
from pathlib import Path

@pytest.fixture
def tmp_raw_wiki(tmp_path):
    """Setup raw/ e wiki/ temporários"""
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    raw.mkdir()
    wiki.mkdir()
    return raw, wiki

@pytest.fixture
def sample_md():
    """Documento de teste"""
    return """---
title: Test Article
topic: cybersecurity
---

# Test

Conteúdo de teste.
"""
```

## Limiar de cobertura

- **Unit:** 80%+
- **Integration:** 60%+
- **Overall:** 70%+

Command:
```bash
pytest --cov=kb --cov-report=html
```

## Rodando testes

```bash
# Todos
pytest

# Unit apenas
pytest tests/unit/

# Integration
pytest tests/integration/

# Um arquivo
pytest tests/unit/test_compile.py::test_compile_file_creates_wiki_article

# Com output
pytest -v -s
```

## Mocking

**LLM chat:** Mock `kb.client.chat()` para evitar chamadas reais

```python
from unittest.mock import patch

def test_qa_returns_response(monkeypatch):
    monkeypatch.setattr("kb.qa.chat", lambda **kw: "Mock response")
    result = answer("test?")
    assert result == "Mock response"
```

## CI (futuro)

```yaml
# .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -e ".[dev]"
      - run: pytest --cov=kb
```

## Best practices

1. **Fixtures over globals** — use fixtures do pytest
2. **Isolate LLM calls** — mock `kb.client.chat()`
3. **Test edge cases** — empty wiki, malformed markdown, wikilinks quebrados
4. **Integration first** — prioritize end-to-end workflows
5. **No real API calls** — todos os testes devem rodar offline/mocked
