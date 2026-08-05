"""028 B4 — dedup de duplicatas de ingestão (RF-04).

Seam: kb.dedup (find_duplicates, DuplicatePair). Duas chaves de candidatura:
mesma fonte resolvida pelo backfill, ou cosseno alto + similaridade textual
alta. Par temático (fontes distintas, texto distinto) nunca entra.
"""

from kb.dedup import DuplicatePair, find_duplicates


def _vault(tmp_path):
    data = tmp_path / "vault"
    wiki = data / "wiki"
    raw = data / "raw"
    wiki.mkdir(parents=True)
    raw.mkdir(parents=True)
    return data, wiki, raw


def _artigo(wiki, rel, source, corpo):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\ntitle: T\ntopic: x\ntags: []\nsource: {source}\n---\n\n{corpo}\n", encoding="utf-8")
    return p


def _fonte(data, book, nome, corpo="capítulo"):
    d = data / "library" / "area" / book
    d.mkdir(parents=True, exist_ok=True)
    (d / nome).write_text(corpo, encoding="utf-8")


def test_should_pair_two_articles_resolved_to_the_same_source(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _fonte(data, "livro-a", "07-cap.md")
    a = _artigo(wiki, "algorithms/decomposicoes.md", "07-cap.md", "Texto sobre decomposições de matrizes e fatoração.")
    b = _artigo(wiki, "decomposicoes.md", "07-cap.md", "Texto sobre decomposições de matrizes e fatoração levemente editado.")

    [par] = find_duplicates(wiki, data, raw)

    assert isinstance(par, DuplicatePair)
    assert par.survivor == a  # path com topic vence a raiz
    assert par.loser == b
    assert par.reason == "same-source"


def test_should_pair_near_identical_articles_by_cosine_and_text_ratio(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    corpo = "A decomposição LU fatora a matriz em triangular inferior e superior. " * 5
    a = _artigo(wiki, "algorithms/lu.md", "01-a.md", corpo)
    b = _artigo(wiki, "lu.md", "02-b.md", corpo + "Uma frase extra no final.")
    vetores = {a: [1.0, 0.0], b: [0.999, 0.045]}

    [par] = find_duplicates(wiki, data, raw, vectors=vetores)

    assert par.survivor == a
    assert par.loser == b
    assert par.reason == "near-identical"
    assert par.text_ratio is not None and par.text_ratio >= 0.85


def test_should_not_pair_thematic_neighbors_with_different_text(tmp_path):
    """Cosseno alto + texto diferente = par temático — intocável (veto do ADR)."""
    data, wiki, raw = _vault(tmp_path)
    a = _artigo(wiki, "algorithms/bst-otima.md", "01-a.md", "Árvore de busca binária ótima com programação dinâmica e probabilidades de acesso.")
    b = _artigo(wiki, "algorithms/bst-probabilidades.md", "02-b.md", "Custo esperado de consultas em árvores balanceadas; derivação alternativa via recorrência distinta e exemplos numéricos próprios.")
    vetores = {a: [1.0, 0.0], b: [0.97, 0.243]}

    pares = find_duplicates(wiki, data, raw, vectors=vetores)

    assert pares == []


def test_should_list_high_cosine_low_ratio_pairs_for_human_review(tmp_path):
    """O mesmo documento vindo de duas URLs gera prosa diferente (caso OWASP:
    cosseno 0,976, ratio 0,248) — não vira candidato automático, mas também
    não pode sumir do relatório: vai para a lista de decisão humana."""
    from kb.dedup import review_candidates

    data, wiki, raw = _vault(tmp_path)
    a = _artigo(wiki, "cybersecurity/recon-a.md", "01-a.md", "Reconhecimento por mecanismos de busca, versão A do texto compilado.")
    b = _artigo(wiki, "cybersecurity/recon-b.md", "02-b.md", "Texto totalmente reescrito na segunda compilação sobre o mesmíssimo assunto de busca.")
    vetores = {a: [1.0, 0.0], b: [0.98, 0.198]}

    [par] = review_candidates(wiki, data, raw, vectors=vetores)

    assert {par.survivor, par.loser} == {a, b}
    assert par.reason == "review"
    assert par.cosine is not None and par.cosine >= 0.95
    assert par.text_ratio is not None and par.text_ratio < 0.85


def test_should_not_review_pairs_already_caught_as_duplicates(tmp_path):
    from kb.dedup import review_candidates

    data, wiki, raw = _vault(tmp_path)
    _fonte(data, "livro-a", "07-cap.md")
    a = _artigo(wiki, "algorithms/x.md", "07-cap.md", "Um texto qualquer.")
    b = _artigo(wiki, "x.md", "07-cap.md", "Outro texto bem diferente do primeiro.")
    vetores = {a: [1.0, 0.0], b: [0.99, 0.14]}

    assert review_candidates(wiki, data, raw, vectors=vetores) == []


def test_should_prefer_longer_article_when_both_lack_topic_dir(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _fonte(data, "livro-a", "09-cap.md")
    curto = _artigo(wiki, "curto.md", "09-cap.md", "Pouco texto.")
    longo = _artigo(wiki, "longo.md", "09-cap.md", "Muito mais texto aqui, com detalhes e exemplos. " * 10)

    [par] = find_duplicates(wiki, data, raw)

    assert par.survivor == longo
    assert par.loser == curto
