import pytest


@pytest.fixture
def tmp_raw_wiki(tmp_path, monkeypatch):
    """Setup raw/ e wiki/ temporários para testes com monkeypatch global"""
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    raw.mkdir()
    wiki.mkdir()

    # Criar subdiretórios de tópicos na wiki
    for topic in ["cybersecurity", "ai", "python", "typescript"]:
        (wiki / topic).mkdir()

    # Monkeypatch das variáveis globais
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.qa.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.heal.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.lint.WIKI_DIR", wiki)

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
