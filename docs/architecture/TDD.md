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
def test_compile_file_creates_wiki_article(tmp_path, monkeypatch):
    # Arrange
    raw_dir = tmp_path / "raw"
    wiki_dir = tmp_path / "wiki"
    raw_dir.mkdir()
    wiki_dir.mkdir()

    raw_file = raw_dir / "test.md"
    raw_file.write_text("# Teste\nConteúdo de teste")

    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki_dir)
    monkeypatch.setattr("kb.compile.chat", lambda *args, **kwargs: """---\ntitle: Test Article\ntopic: general\ntags: [test]\nsource: test.md\n---\n\n# Test Article\n\nConteúdo.\n""")

    # Act
    result = compile_file(raw_file)

    # Assert
    assert result.exists()
    assert result.parent == wiki_dir / "general"
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
topic: general
---

# Test

Conteúdo de teste.
"""
```

## Limiar de cobertura

- **Unit:** 80%+
- **Integration:** 60%+
- **Overall:** 70%+ (piso; a suíte está em 92% desde 2026-07-31)

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

## CI

`.github/workflows/tests.yml` roda a suíte em Python 3.11, 3.12 e 3.13 a cada push e PR. Há ainda `kb-doc-governance.yml` (doc-gate) e `kb-jobs-and-health-gate.yml` (gates operacionais).

## Isolamento de estado — inegociável

Toda fixture que toca a wiki tem de isolar **todo** o `kb_state`, não só `WIKI_DIR`. Em 2026-07-29 a suíte destruiu o índice de embeddings do vault real: `tmp_wiki` isolava a wiki mas não o `STATE_DIR`, e um teste de `heal` reconstruiu o índice a partir da wiki temporária de 1 artigo, gravando por cima dos 1.037 vetores do usuário.

- `tmp_wiki` e `tmp_raw_wiki` isolam `STATE_DIR`, manifest, knowledge, learnings, claims, audit e `tracking.DB_PATH`.
- `tests/unit/test_conftest_isolation.py` é o guarda dessa propriedade — não remova.
- Fixtures `autouse` do `conftest.py` desligam efeitos de rede que entraram por default no produto: `KB_INDEX_AUTO_REFRESH=0` e `KB_RERANK_DEPTH=0`. Teste que verifica o default remove a variável explicitamente.

Sintoma de que isso quebrou: a suíte, que roda em segundos, passa a levar dezenas de segundos — é a assinatura de chamada real ao provider.

## Best practices

1. **Fixtures over globals** — use fixtures do pytest
2. **Isolate LLM calls** — mock `kb.client.chat()`
3. **Test edge cases** — empty wiki, malformed markdown, wikilinks quebrados
4. **Integration first** — prioritize end-to-end workflows
5. **No real API calls** — todos os testes devem rodar offline/mocked
6. **Medir pela superfície que o usuário usa** — teste que chama a função não prova que a CLI expõe o caminho. Sete features de retrieval mediram +42% de MRR por um parâmetro que nenhum comando passava (2026-07-30).
