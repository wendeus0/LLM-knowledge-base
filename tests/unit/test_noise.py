"""RED — feature 011-corpus-noise-filter (RF-03, RF-04).

Seam: kb.noise (classify_chapter, load_taxonomy).
Categorias esperadas (slugs): agradecimentos, dedicatoria, prefacio, elogios,
encerramento, colofao, sobre_o_autor, copyright, indice.
"""

from kb.noise import classify_chapter, load_taxonomy


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
