"""RED — feature 013-context-budget (RF-01, RF-02, RF-03, RF-06 + casos de erro).

Seams: kb.router.cap_text e montagem de contexto; kb.config.get_retrieval_profile.
"""

import pytest

from kb.config import get_retrieval_profile
from kb.router import cap_text

TRUNC_MARKER = "[... truncado]"


def test_should_cut_at_paragraph_boundary_with_marker():
    # RED: falha até 013-context-budget ser implementada (RF-01)
    # Trabalhado à mão: p1 (20 chars) + \n\n + p2 (30 chars) + \n\n + p3;
    # cap=40 → só p1 cabe inteiro antes da fronteira seguinte.
    text = "a" * 20 + "\n\n" + "b" * 30 + "\n\n" + "c" * 10
    result = cap_text(text, 40)
    assert result.startswith("a" * 20)
    assert "b" not in result
    assert result.rstrip().endswith(TRUNC_MARKER)


def test_should_keep_article_intact_when_below_cap():
    # RED: falha até 013-context-budget ser implementada (RF-01)
    text = "parágrafo um\n\nparágrafo dois"
    assert cap_text(text, 4000) == text
    assert TRUNC_MARKER not in cap_text(text, 4000)


def test_should_hard_cut_when_single_paragraph_exceeds_cap():
    # RED: falha até 013-context-budget ser implementada (caso de erro: parágrafo gigante)
    text = "x" * 500  # sem \n\n
    result = cap_text(text, 100)
    assert TRUNC_MARKER in result
    assert len(result) <= 100 + len("\n\n" + TRUNC_MARKER)


def test_should_expose_profiles_with_planned_parameters():
    # RED: falha até 013-context-budget ser implementada (RF-03)
    fast = get_retrieval_profile("fast")
    deep = get_retrieval_profile("deep")
    paper = get_retrieval_profile("paper")
    article = get_retrieval_profile("article")
    assert fast["top_k"] == 3 and fast["doc_chars"] == 4000
    assert deep["top_k"] == 5 and deep["doc_chars"] == 8000
    assert paper["top_k"] == 3 and paper["traverse"] is False
    assert article["top_k"] == 5 and article["traverse"] is True


def test_should_reject_unknown_profile_listing_valid_ones():
    # RED: falha até 013-context-budget ser implementada (caso de erro: perfil desconhecido)
    with pytest.raises(ValueError, match="fast"):
        get_retrieval_profile("turbo")


def test_should_override_doc_chars_via_env(monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-06)
    monkeypatch.setenv("KB_QA_DOC_CHARS", "1234")
    assert get_retrieval_profile("fast")["doc_chars"] == 1234
    assert get_retrieval_profile("deep")["doc_chars"] == 1234


def test_should_cap_seed_articles_in_wiki_context(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-02: seeds capados)
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    long_body = ("Conteúdo técnico relevante sobre resiliencia. " * 200).strip()
    (wiki / "artigo-longo.md").write_text(
        f"---\ntitle: Artigo Longo\n---\n\n{long_body}", encoding="utf-8"
    )
    monkeypatch.setattr("kb.router.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    from kb.router import _build_wiki_context

    parts = _build_wiki_context("resiliencia", top_k=1, traverse=False, doc_chars=500)
    assert len(parts) == 1
    assert TRUNC_MARKER in parts[0]
    assert len(parts[0]) < 700  # 500 + cabeçalho + marcador


def test_should_cap_documents_in_raw_context(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-02: rota raw capada)
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "doc-longo.md").write_text(
        ("Notas cruas sobre resiliencia em sistemas. " * 200).strip(), encoding="utf-8"
    )
    monkeypatch.setattr("kb.router.RAW_DIR", raw)
    from kb.router import _build_raw_context

    parts = _build_raw_context("resiliencia", top_k=1, doc_chars=500)
    assert len(parts) == 1
    assert TRUNC_MARKER in parts[0]
    assert len(parts[0]) < 700
