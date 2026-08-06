"""028 B6/B7 — normalização determinística e assign restrito de topics.

Seam: kb.topics (normalize_variants, propose_topics, apply_topic).
Taxonomia fechada pelo dono em 2026-08-05 (10 canônicos) + mapa de variantes.
"""

from kb.topics import VARIANT_MAP, apply_topic, normalize_variants, propose_topics

TAXONOMIA = [
    "algorithms", "ai", "python", "learning", "cybersecurity",
    "harness", "software-architecture", "data", "testing", "operations",
]


def _artigo(wiki, rel, topic, corpo="Corpo.\n"):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f'---\ntitle: "Título: com dois-pontos"\ntopic: {topic}\ntags: [a, b]\nsource: x.md\n---\n\n{corpo}',
        encoding="utf-8",
    )
    return p


def test_should_map_the_approved_variants_to_canonical_topics():
    assert VARIANT_MAP["architecture"] == "software-architecture"
    assert VARIANT_MAP["ddd"] == "software-architecture"
    assert VARIANT_MAP["domain-driven-design"] == "software-architecture"
    assert VARIANT_MAP["hexagonal"] == "software-architecture"
    assert VARIANT_MAP["data-engineering"] == "data"
    assert VARIANT_MAP["observability"] == "operations"
    assert VARIANT_MAP["devops"] == "operations"
    assert VARIANT_MAP["tensorflow"] == "ai"
    assert VARIANT_MAP["mathematics"] == "algorithms"
    assert VARIANT_MAP["geral"] == "general"


def test_should_propose_normalization_only_for_variant_topics(tmp_path):
    wiki = tmp_path / "wiki"
    a = _artigo(wiki, "artigo-ddd.md", "ddd")
    _artigo(wiki, "artigo-ok.md", "algorithms")
    _artigo(wiki, "_pipeline/nota.md", "ddd")

    propostas = normalize_variants(wiki)

    assert [(p.article, p.old, p.new) for p in propostas] == [(a, "ddd", "software-architecture")]


def test_should_rewrite_only_the_topic_line_preserving_everything_else(tmp_path):
    wiki = tmp_path / "wiki"
    artigo = _artigo(wiki, "artigo.md", "observability", corpo="Linha 1.\n\ntopic: falso no corpo\n")
    antes = artigo.read_text(encoding="utf-8")

    apply_topic(artigo, "operations")

    depois = artigo.read_text(encoding="utf-8")
    assert "topic: operations" in depois
    assert "topic: observability" not in depois
    assert "topic: falso no corpo" in depois  # corpo intocado
    assert depois.replace("topic: operations", "topic: observability", 1) == antes


def test_should_propose_topics_only_within_the_taxonomy(tmp_path):
    wiki = tmp_path / "wiki"
    a = _artigo(wiki, "circuit-breaker.md", "general", corpo="Padrão de estabilidade em produção.\n")
    b = _artigo(wiki, "fora.md", "general", corpo="Outro artigo.\n")

    def chat(messages, **kwargs):
        pergunta = messages[-1]["content"]
        if "circuit-breaker" in pergunta:
            return "operations"
        return "categoria-inventada"

    propostas = propose_topics([a, b], TAXONOMIA, chat_fn=chat)

    por_artigo = {p.article: p for p in propostas}
    assert por_artigo[a].new == "operations"
    assert por_artigo[a].rejected is False
    assert por_artigo[b].new is None
    assert por_artigo[b].rejected is True  # fora da taxonomia nunca é gravável


def test_should_not_touch_articles_that_already_have_canonical_topic(tmp_path):
    wiki = tmp_path / "wiki"
    _artigo(wiki, "ai/pronto.md", "ai")

    assert normalize_variants(wiki) == []
