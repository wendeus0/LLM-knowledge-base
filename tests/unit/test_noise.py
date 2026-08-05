"""Feature 011-corpus-noise-filter (RF-03, RF-04) + 027-noise-retro (RF-01..RF-03).

Seam: kb.noise (classify_chapter, load_taxonomy, scan_corpus, NoiseCandidate).
Categorias esperadas (slugs): agradecimentos, dedicatoria, prefacio, elogios,
encerramento, colofao, sobre_o_autor, copyright, indice.
"""

import json

from kb.noise import NoiseCandidate, classify_chapter, load_taxonomy, scan_corpus


def _paths(candidates):
    assert all(isinstance(c, NoiseCandidate) for c in candidates), (
        "scan_corpus deve devolver candidatos estruturados"
    )
    return [c.path for c in candidates]


def test_should_classify_pt_noise_titles_by_category():
    # RED: falha até 011-corpus-noise-filter ser implementada
    assert classify_chapter("Agradecimentos") == "agradecimentos"
    assert classify_chapter("Dedicatória") == "dedicatoria"
    assert classify_chapter("Prefácio") == "prefacio"
    assert classify_chapter("Elogios") == "elogios"
    assert classify_chapter("Posfácio") == "encerramento"
    assert classify_chapter("Sobre o autor") == "sobre_o_autor"


def test_should_classify_en_noise_titles_by_category():
    # RED: falha até 011-corpus-noise-filter ser implementada
    assert classify_chapter("Acknowledgments") == "agradecimentos"
    assert classify_chapter("Preface") == "prefacio"
    assert classify_chapter("Foreword") == "prefacio"
    assert classify_chapter("Praise for This Book") == "elogios"
    assert classify_chapter("Epilogue") == "encerramento"
    assert classify_chapter("About the Author") == "sobre_o_autor"
    assert classify_chapter("Colophon") == "colofao"


def test_should_keep_chapter_when_title_is_ambiguous():
    # RED: falha até 011-corpus-noise-filter ser implementada
    # (a taxonomia default deve existir e ser não-vazia; na dúvida, mantém)
    taxonomy = load_taxonomy()
    assert taxonomy, "taxonomia default deve ser não-vazia"
    assert classify_chapter("Reflexões sobre a jornada", taxonomy) is None
    assert classify_chapter("Capítulo 7 — Retrieval híbrido", taxonomy) is None


def test_should_keep_conclusao_as_content():
    # RED: falha até 011-corpus-noise-filter ser implementada
    # Decisão A do dono (2026-07-15): Conclusão/Considerações finais são conteúdo.
    taxonomy = load_taxonomy()
    assert taxonomy, "taxonomia default deve ser não-vazia"
    assert classify_chapter("Conclusão", taxonomy) is None
    assert classify_chapter("Considerações finais", taxonomy) is None
    assert classify_chapter("Conclusion", taxonomy) is None


def test_should_match_case_and_accent_insensitive():
    # RED: falha até 011-corpus-noise-filter ser implementada
    assert classify_chapter("AGRADECIMENTOS") == "agradecimentos"
    assert classify_chapter("prefacio") == "prefacio"
    assert classify_chapter("  Dedicatoria  ") == "dedicatoria"


def test_should_keep_title_with_noise_word_mid_sentence():
    # RED: falha até 011-corpus-noise-filter ser implementada
    # Falso-amigo: termo da taxonomia no meio de título de conteúdo não corta.
    taxonomy = load_taxonomy()
    assert taxonomy, "taxonomia default deve ser não-vazia"
    assert classify_chapter("O que os agradecimentos revelam sobre redes sociais", taxonomy) is None
    assert classify_chapter("Why every preface lies", taxonomy) is None


def test_should_extend_taxonomy_from_vault_override(tmp_path):
    # RED: falha até 011-corpus-noise-filter ser implementada
    override = tmp_path / "kb.toml"
    override.write_text(
        '[noise]\nextra = { nota_do_tradutor = ["nota do tradutor", "translator\'s note"] }\n',
        encoding="utf-8",
    )
    taxonomy = load_taxonomy(override_path=override)
    assert classify_chapter("Nota do tradutor", taxonomy) == "nota_do_tradutor"
    # defaults continuam valendo com override presente
    assert classify_chapter("Agradecimentos", taxonomy) == "agradecimentos"


def _write_book_metadata(raw_dir, chapters):
    book_dir = raw_dir / "books" / "livro"
    book_dir.mkdir(parents=True)
    (book_dir / "metadata.json").write_text(
        json.dumps({"chapters": chapters}), encoding="utf-8"
    )
    return book_dir


class TestChapterPathContainment:
    """F-05: `chapters[].file` de metadata.json é entrada não-confiável."""

    def test_should_ignore_chapter_file_escaping_the_book_dir(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        outside = tmp_path / "secrets"
        outside.mkdir()
        (outside / "id_rsa.md").write_text("PRIVATE KEY", encoding="utf-8")
        _write_book_metadata(
            raw,
            [{"title": "Agradecimentos", "file": "../../../secrets/id_rsa.md"}],
        )

        candidates = scan_corpus(raw, wiki)

        assert candidates == []
        assert (outside / "id_rsa.md").exists()

    def test_should_ignore_absolute_chapter_file(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        target = tmp_path / "etc-passwd.md"
        target.write_text("root:x:0:0", encoding="utf-8")
        _write_book_metadata(raw, [{"title": "Copyright", "file": str(target)}])

        assert scan_corpus(raw, wiki) == []

    def test_should_keep_chapter_file_inside_the_book_dir(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        book_dir = _write_book_metadata(
            raw, [{"title": "Agradecimentos", "file": "ch01.md"}]
        )
        (book_dir / "ch01.md").write_text("obrigado", encoding="utf-8")

        assert _paths(scan_corpus(raw, wiki)) == [book_dir / "ch01.md"]

    def test_should_not_mark_escaping_chapter_file_as_noisy_source(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        _write_book_metadata(
            raw, [{"title": "Agradecimentos", "file": "../../outro.md"}]
        )
        (wiki / "artigo.md").write_text(
            "---\ntitle: Artigo de conteúdo\nsource: ../../outro.md\n---\n\ncorpo",
            encoding="utf-8",
        )

        assert scan_corpus(raw, wiki) == []


def _write_library_book(library_dir, area, book, chapters, com_arquivos=True):
    book_dir = library_dir / area / book
    book_dir.mkdir(parents=True)
    (book_dir / "metadata.json").write_text(
        json.dumps({"book_title": book, "chapters": chapters}), encoding="utf-8"
    )
    if com_arquivos:
        for chapter in chapters:
            (book_dir / chapter["file"]).write_text("conteúdo", encoding="utf-8")
    return book_dir


def _write_article(wiki, rel, title, source):
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntopic: general\nsource: {source}\n---\n\ncorpo",
        encoding="utf-8",
    )
    return path


class TestScanMultiRoot:
    """027 RF-01: o scan cobre raw/books/ E library/<área>/<livro>/."""

    def test_should_find_wiki_article_derived_from_a_noisy_library_chapter(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        _write_library_book(
            library, "software", "livro-a", [{"title": "Preface", "file": "04-preface.md"}]
        )
        artigo = _write_article(wiki, "prefacio-e-visao-geral.md", "Prefácio e visão geral", "04-preface.md")
        _write_article(wiki, "capitulo-real.md", "Capítulo real", "07-content.md")

        candidates = scan_corpus(raw, wiki, library_dir=library)

        assert artigo in _paths(candidates)
        assert wiki / "capitulo-real.md" not in _paths(candidates)

    def test_should_not_list_library_source_chapters_as_candidates(self, tmp_path):
        """Capítulo-fonte de library/ nunca é candidato a move (invariante 2 do DOMAIN)."""
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        book_dir = _write_library_book(
            library, "software", "livro-a", [{"title": "Copyright", "file": "02-copyright.md"}]
        )

        candidates = scan_corpus(raw, wiki, library_dir=library)

        assert book_dir / "02-copyright.md" not in _paths(candidates)

    def test_should_scan_both_roots_in_the_same_pass(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        book_raw = _write_book_metadata(raw, [{"title": "Agradecimentos", "file": "ch01.md"}])
        (book_raw / "ch01.md").write_text("obrigado", encoding="utf-8")
        _write_library_book(
            library, "ai", "livro-b", [{"title": "Index", "file": "20-index.md"}]
        )
        artigo = _write_article(wiki, "indice-remissivo.md", "Índice conceitual", "20-index.md")

        paths = _paths(scan_corpus(raw, wiki, library_dir=library))

        assert book_raw / "ch01.md" in paths
        assert artigo in paths

    def test_should_apply_path_containment_to_library_metadata(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        (tmp_path / "fora.md").write_text("segredo", encoding="utf-8")
        _write_library_book(
            library,
            "software",
            "livro-mau",
            [{"title": "Prefácio", "file": "../../../fora.md"}],
            com_arquivos=False,
        )
        _write_article(wiki, "artigo.md", "Artigo", "../../../fora.md")

        assert scan_corpus(raw, wiki, library_dir=library) == []


class TestCandidateStructure:
    """027 RF-02: o candidato carrega livro, título do capítulo e categoria."""

    def test_should_qualify_article_candidate_with_book_and_chapter_title(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        _write_library_book(
            library, "software", "learning-ddd", [{"title": "Dedication", "file": "03-dedications.md"}]
        )
        artigo = _write_article(wiki, "dedicatorias.md", "Dedicatórias", "03-dedications.md")

        [candidate] = scan_corpus(raw, wiki, library_dir=library)

        assert candidate.path == artigo
        assert candidate.kind == "article"
        assert candidate.category == "dedicatoria"
        assert candidate.book == "learning-ddd"
        assert candidate.chapter_title == "Dedication"

    def test_should_attach_the_mirrored_summary_when_it_exists(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        _write_library_book(
            library, "software", "livro-a", [{"title": "Preface", "file": "04-preface.md"}]
        )
        _write_article(wiki, "ai/prefacio.md", "Prefácio", "04-preface.md")
        summary = wiki / "_summaries" / "ai" / "prefacio.md"
        summary.parent.mkdir(parents=True)
        summary.write_text("resumo", encoding="utf-8")

        [candidate] = scan_corpus(raw, wiki, library_dir=library)

        assert candidate.summary == summary

    def test_should_flag_provenance_as_ambiguous_when_basename_collides_across_books(self, tmp_path):
        """Sem manifest, o basename não diz de QUAL livro o artigo veio — o
        relatório precisa dizer isso em vez de atribuir o primeiro livro varrido."""
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        library = tmp_path / "library"
        wiki.mkdir()
        _write_library_book(
            library, "software", "livro-a", [{"title": "Index", "file": "20-index.md"}]
        )
        _write_library_book(
            library, "software", "livro-b", [{"title": "Index", "file": "20-index.md"}]
        )
        _write_article(wiki, "indice.md", "Índice conceitual", "20-index.md")

        [candidate] = scan_corpus(raw, wiki, library_dir=library)

        assert candidate.category == "indice"
        assert "livro-a" in candidate.book and "livro-b" in candidate.book

    def test_should_mark_title_match_without_book_provenance(self, tmp_path):
        raw = tmp_path / "raw"
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        _write_article(wiki, "sumario.md", "Índice remissivo", "qualquer.md")

        [candidate] = scan_corpus(raw, wiki)

        assert candidate.kind == "article"
        assert candidate.category == "indice"
        assert candidate.book is None
