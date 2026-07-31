import pytest


def pytest_addoption(parser):
    try:
        import pytest_cov.plugin  # noqa: F401
    except ImportError:
        group = parser.getgroup("cov-compat")
        group.addoption("--cov", action="append", default=[])
        group.addoption("--cov-report", action="append", default=[])


@pytest.fixture(autouse=True)
def _no_side_effect_llm_calls(monkeypatch):
    """Nenhum teste chama provider real.

    A feature 015 pendurou refresh de índice no fim de compile/heal/qa. Sem este
    guard, esses testes fazem probe do servidor e chegam a embedar de verdade —
    a suíte passou de 4s para 80s antes de alguém notar.

    Testes que exercitam o refresh removem a variável explicitamente.

    Mesmo motivo para o rerank: ligá-lo por padrão no QA fez os testes de perfil
    baterem no provider de reordenação, 4s por teste.
    """
    monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")
    monkeypatch.setenv("KB_RERANK_DEPTH", "0")


@pytest.fixture(autouse=True)
def _state_dir_never_points_at_real_vault(tmp_path_factory, monkeypatch):
    """Piso de isolamento: `STATE_DIR` nunca é o do usuário durante a suíte.

    As fixtures de wiki já isolam o estado, mas há testes que monkeypatcham só
    `kb.search.WIKI_DIR` e dependiam do kill-switch de env acima para não
    escrever no vault. Foi exatamente essa combinação — isolar a wiki e esquecer
    o estado — que destruiu o índice de embeddings real em 2026-07-29. Env é
    kill-switch; isolamento tem de ser estrutural.

    Fixture que isola de propósito sobrescreve isto — vem depois na ordem.
    """
    piso = tmp_path_factory.mktemp("kb_state_piso")
    monkeypatch.setattr("kb.config.STATE_DIR", piso, raising=False)


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
    claims_path = state_dir / "claims.jsonl"

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
    monkeypatch.setattr("kb.router.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.core.tracking.DB_PATH", state_dir / "tracking.db")
    monkeypatch.setattr("kb.state.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.state.KNOWLEDGE_PATH", knowledge_path)
    monkeypatch.setattr("kb.state.LEARNINGS_PATH", learnings_path)
    monkeypatch.setattr("kb.state.MANIFEST_PATH", manifest_path)
    monkeypatch.setattr("kb.config.CLAIMS_PATH", claims_path)
    monkeypatch.setattr("kb.claims.CLAIMS_PATH", claims_path)
    monkeypatch.setattr("kb.config.AUDIT_PATH", state_dir / "audit.jsonl")

    return raw, wiki


@pytest.fixture
def tmp_wiki(tmp_path, monkeypatch):
    """Setup wiki/ com estrutura de tópicos e monkeypatch de WIKI_DIR.

    Isola também o estado do vault: qualquer comando que escreva em kb_state/
    (índice de embeddings, manifesto, tracking) precisa cair no tmp_path, nunca
    no vault real do usuário.
    """
    wiki = tmp_path / "wiki"
    state_dir = tmp_path / "kb_state"
    wiki.mkdir()
    state_dir.mkdir()
    for topic in ["cybersecurity", "ai", "python", "typescript"]:
        (wiki / topic).mkdir()

    # Monkeypatch WIKI_DIR para funções que o usam diretamente
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.heal.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.lint.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.router.WIKI_DIR", wiki)

    monkeypatch.setattr("kb.config.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.state.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", state_dir / "manifest.json")
    monkeypatch.setattr("kb.state.MANIFEST_PATH", state_dir / "manifest.json")
    monkeypatch.setattr("kb.config.KNOWLEDGE_PATH", state_dir / "knowledge.json")
    monkeypatch.setattr("kb.state.KNOWLEDGE_PATH", state_dir / "knowledge.json")
    monkeypatch.setattr("kb.config.LEARNINGS_PATH", state_dir / "learnings.json")
    monkeypatch.setattr("kb.state.LEARNINGS_PATH", state_dir / "learnings.json")
    monkeypatch.setattr("kb.config.CLAIMS_PATH", state_dir / "claims.jsonl")
    monkeypatch.setattr("kb.claims.CLAIMS_PATH", state_dir / "claims.jsonl")
    monkeypatch.setattr("kb.config.AUDIT_PATH", state_dir / "audit.jsonl")
    monkeypatch.setattr("kb.core.tracking.DB_PATH", state_dir / "tracking.db")

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
