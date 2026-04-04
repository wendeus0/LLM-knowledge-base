from kb.router import build_context, decide_route
from kb.state import add_learning, upsert_knowledge


def test_should_route_general_question_to_wiki(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (wiki / "ai" / "ml.md").write_text("# ML\nMachine learning é IA.")

    decision, context = build_context("O que é machine learning?")

    assert decision.route == "wiki"
    assert context


def test_should_route_original_source_question_to_raw(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (raw / "capitulo.md").write_text("Texto original do capítulo sobre redes neurais.")

    decision, context = build_context("Quero o texto original do capítulo")

    assert decision.route == "raw"
    assert context


def test_should_route_knowledge_question_to_knowledge_store(tmp_raw_wiki):
    upsert_knowledge({"title": "XSS", "summary_text": "Resumo compilado sobre XSS", "topic": "cybersecurity"})

    decision, context = build_context("Mostre o resumo compilado de XSS")

    assert decision.route == "knowledge"
    assert context


def test_should_route_learning_question_to_learnings_store(tmp_raw_wiki):
    add_learning("retrieval", "Preferir wiki para perguntas gerais", source="qa")

    decision, context = build_context("O que você aprendeu sobre retrieval?")

    assert decision.route == "learnings"
    assert context


def test_should_classify_route_deterministically():
    assert decide_route("Mostre o texto original da fonte").route == "raw"
    assert decide_route("Qual resumo compilado existe?").route == "knowledge"
    assert decide_route("O que você aprendeu?").route == "learnings"
    assert decide_route("Explique XSS").route == "wiki"
