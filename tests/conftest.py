import pytest


def pytest_addoption(parser):
    try:
        import pytest_cov.plugin  # noqa: F401
    except ImportError:
        group = parser.getgroup("cov-compat")
        group.addoption("--cov", action="append", default=[])
        group.addoption("--cov-report", action="append", default=[])


@pytest.fixture
def tmp_raw_wiki(tmp_path, monkeypatch):
    """Setup raw/, wiki/ e outputs/ temporários para testes com monkeypatch global"""
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    outputs = tmp_path / "outputs"
    state_dir = tmp_path / "kb_state"
    raw.mkdir()
    wiki.mkdir()
    outputs.mkdir()
    state_dir.mkdir()

    # Criar subdiretórios de tópicos na wiki
    for topic in ["cybersecurity", "ai", "python", "typescript"]:
        (wiki / topic).mkdir()

    knowledge_path = state_dir / "knowledge.json"
    learnings_path = state_dir / "learnings.json"
    manifest_path = state_dir / "manifest.json"

    # Monkeypatch das variáveis globais
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs)
    monkeypatch.setattr("kb.config.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.config.KNOWLEDGE_PATH", knowledge_path)
    monkeypatch.setattr("kb.config.LEARNINGS_PATH", learnings_path)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", manifest_path)
    monkeypatch.setattr("kb.compile.RAW_DIR", raw)
    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.qa.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.heal.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.lint.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.router.RAW_DIR", raw)
    monkeypatch.setattr("kb.state.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.state.KNOWLEDGE_PATH", knowledge_path)
    monkeypatch.setattr("kb.state.LEARNINGS_PATH", learnings_path)
    monkeypatch.setattr("kb.state.MANIFEST_PATH", manifest_path)

    return raw, wiki


@pytest.fixture
def tmp_wiki(tmp_path, monkeypatch):
    """Setup wiki/ com estrutura de tópicos e monkeypatch de WIKI_DIR"""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    for topic in ["cybersecurity", "ai", "python", "typescript"]:
        (wiki / topic).mkdir()

    # Monkeypatch WIKI_DIR para funções que o usam diretamente
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.heal.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.lint.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)

    return wiki


@pytest.fixture
def sample_md():
    """Documento de teste com structure básica"""
    return """---
title: Test Article
topic: cybersecurity
---

# Test Article

Conteúdo de teste sobre segurança.

## Subtítulo

Mais detalhes sobre o tópico.
"""


@pytest.fixture
def sample_xss_md():
    """Documento sobre XSS para teste de compile"""
    return """# O que é XSS?

XSS (Cross-Site Scripting) é uma vulnerabilidade web comum.

## Tipos de XSS

- Refletido
- Armazenado
- DOM-based

## Como prevenir

Sempre sanitizar entrada do usuário.
"""


@pytest.fixture
def monkeypatch_env(monkeypatch):
    """Setup variáveis de ambiente para testes"""
    monkeypatch.setenv("KB_API_KEY", "test-key")
    monkeypatch.setenv("KB_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("KB_MODEL", "test-model")
    return monkeypatch
