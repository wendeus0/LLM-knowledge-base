"""RED — feature 011-corpus-noise-filter (RF-03, RF-04).

Seam: kb.noise (classify_chapter, load_taxonomy).
Categorias esperadas (slugs): agradecimentos, dedicatoria, prefacio, elogios,
encerramento, colofao, sobre_o_autor, copyright, indice.
"""

import json

from kb.noise import classify_chapter, load_taxonomy, scan_corpus


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

        assert scan_corpus(raw, wiki) == [book_dir / "ch01.md"]

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
