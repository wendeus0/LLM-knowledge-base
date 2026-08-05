"""Classificação e limpeza de capítulos-ruído do corpus (feature 011-corpus-noise-filter).

Ruído = capítulo sem conteúdo de conhecimento: agradecimentos, dedicatória,
prefácio, elogios, encerramento (epílogo/posfácio), colofão, sobre o autor,
copyright, índice remissivo. Conclusão/Considerações finais são conteúdo e
nunca entram na taxonomia default (decisão do dono, 2026-07-15).
"""

import json
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NoiseCandidate:
    """Candidato a ruído com a proveniência que o relatório de revisão exige."""

    path: Path
    kind: str  # "chapter" (fonte em raw/books) | "article" (wiki)
    category: str
    book: str | None = None
    chapter_title: str | None = None
    summary: Path | None = None

DEFAULT_TAXONOMY: dict[str, list[str]] = {
    "agradecimentos": ["agradecimentos", "agradecimento", "acknowledgments", "acknowledgements", "acknowledgment"],
    "dedicatoria": ["dedicatoria", "dedication"],
    "prefacio": ["prefacio", "preface", "foreword", "prologo do editor"],
    "elogios": ["elogios", "elogios a este livro", "praise", "praise for"],
    "encerramento": ["posfacio", "epilogo", "epilogue", "afterword", "palavras finais", "closing words"],
    "colofao": ["colofao", "colophon"],
    "sobre_o_autor": ["sobre o autor", "sobre a autora", "sobre os autores", "about the author", "about the authors"],
    "copyright": ["copyright", "pagina de copyright", "direitos autorais", "avisos legais", "ficha catalografica", "creditos"],
    "indice": ["indice remissivo", "indice alfabetico", "index"],
    "capa": ["capa", "pagina de titulo", "cover", "title page", "capa do documento"],
}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.strip().casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def load_taxonomy(override_path: Path | None = None) -> dict[str, list[str]]:
    """Taxonomia default + override por vault (`kb.toml`, seção [noise].extra)."""
    taxonomy = {category: list(terms) for category, terms in DEFAULT_TAXONOMY.items()}
    if override_path is None:
        from kb.config import DATA_DIR

        candidate = Path(DATA_DIR) / "kb.toml"
        override_path = candidate if candidate.exists() else None
    if override_path is not None and Path(override_path).exists():
        data = tomllib.loads(Path(override_path).read_text(encoding="utf-8"))
        extra = data.get("noise", {}).get("extra", {})
        for category, terms in extra.items():
            taxonomy.setdefault(category, []).extend(terms)
    return taxonomy


def classify_chapter(title: str, taxonomy: dict[str, list[str]] | None = None) -> str | None:
    """Retorna a categoria de ruído do título, ou None (conteúdo — na dúvida, mantém).

    Match por título inteiro ou por prefixo com fronteira de palavra; termo da
    taxonomia no meio do título não corta (falso-amigo).
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()
    normalized = _normalize(title)
    if not normalized:
        return None
    for category, terms in taxonomy.items():
        for term in terms:
            normalized_term = _normalize(term)
            if normalized == normalized_term or normalized.startswith(normalized_term + " "):
                return category
    return None


def contains_noise_term(title: str, taxonomy: dict[str, list[str]] | None = None) -> bool:
    """Título contém termo da taxonomia sem ser classificável (candidato ambíguo)."""
    if taxonomy is None:
        taxonomy = load_taxonomy()
    normalized = _normalize(title)
    return any(
        _normalize(term) in normalized for terms in taxonomy.values() for term in terms
    )


def split_noise(
    chapters: list[dict], taxonomy: dict[str, list[str]] | None = None
) -> tuple[list[dict], list[dict], list[str]]:
    """Separa capítulos em (conteúdo, excluídos, ambíguos mantidos).

    Título de fallback nunca é classificado; ambíguo = mantido, mas contém
    termo da taxonomia (reportado como "não classificado").
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()
    kept: list[dict] = []
    excluded: list[dict] = []
    ambiguous: list[str] = []
    for chapter in chapters:
        category = None
        title = chapter.get("title") or ""
        if chapter.get("title_source") != "fallback":
            category = classify_chapter(title, taxonomy)
        if category:
            excluded.append({"title": chapter["title"], "category": category})
        else:
            kept.append(chapter)
            if chapter.get("title_source") != "fallback" and contains_noise_term(title, taxonomy):
                ambiguous.append(title)
    return kept, excluded, ambiguous


def _chapter_path_inside_book(metadata_path: Path, chapter_file: str) -> Path | None:
    """Resolve `chapters[].file` dentro do diretório do livro; fora dele, descarta.

    `metadata.json` é estado do vault e pode ter sido adulterado; sem esta checagem
    um `file` com `../` ou absoluto faz o `noise apply` mover arquivo de qualquer
    lugar do disco para `archive/`.
    """
    candidate_file = Path(chapter_file)
    if candidate_file.is_absolute() or ".." in candidate_file.parts:
        return None
    book_dir = metadata_path.parent
    candidate = book_dir / candidate_file
    try:
        resolved = candidate.resolve()
        book_root = book_dir.resolve()
    except OSError:
        return None
    if resolved == book_root or not resolved.is_relative_to(book_root):
        return None
    return candidate


def _noisy_chapters(metadata_globs, taxonomy):
    """Mapa `basename do capítulo → (livros, título, categoria)` das raízes dadas.

    A colisão de basename entre livros é benigna para a CLASSIFICAÇÃO — o slug
    embute o título (`04-preface.md` é prefácio em qualquer livro) — mas não
    para a proveniência: sem manifest, o basename não diz de qual livro o
    artigo veio, e o relatório precisa listar todos os candidatos.
    """
    noisy: dict[str, tuple[list[str], str, str]] = {}
    chapter_paths: list[tuple[Path, str]] = []
    for metadata_path in metadata_globs:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        book = metadata.get("book_title") or metadata_path.parent.name
        for chapter in metadata.get("chapters", []):
            title = chapter.get("title") or ""
            category = classify_chapter(title, taxonomy)
            if not category:
                continue
            chapter_file = chapter.get("file")
            if not chapter_file:
                continue
            chapter_path = _chapter_path_inside_book(metadata_path, chapter_file)
            if chapter_path is None:
                continue
            if chapter_file in noisy:
                books = noisy[chapter_file][0]
                if book not in books:
                    books.append(book)
            else:
                noisy[chapter_file] = ([book], title, category)
            chapter_paths.append((chapter_path, category))
    return noisy, chapter_paths


def _summary_mirror(article: Path, wiki_dir: Path) -> Path | None:
    candidate = Path(wiki_dir) / "_summaries" / article.relative_to(wiki_dir)
    return candidate if candidate.exists() else None


def scan_corpus(
    raw_dir: Path,
    wiki_dir: Path,
    library_dir: Path | None = None,
    taxonomy: dict[str, list[str]] | None = None,
) -> list[NoiseCandidate]:
    """Candidatos a ruído já ingeridos, com a proveniência que a revisão exige.

    Duas raízes de metadados: `raw/books/*/` (fila de entrada — os capítulos-
    ruído dela SÃO candidatos a move) e `library/*/…/` (acervo — os capítulos
    ficam intactos e só qualificam os artigos da wiki derivados deles).
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()
    candidates: list[NoiseCandidate] = []

    raw_globs = sorted(Path(raw_dir).glob("books/*/metadata.json"))
    noisy_raw, raw_chapter_paths = _noisy_chapters(raw_globs, taxonomy)
    for chapter_path, category in raw_chapter_paths:
        if chapter_path.exists():
            candidates.append(
                NoiseCandidate(path=chapter_path, kind="chapter", category=category)
            )

    noisy_library: dict[str, tuple[str, str, str]] = {}
    if library_dir is not None:
        library_globs = sorted(Path(library_dir).glob("*/metadata.json")) + sorted(
            Path(library_dir).glob("*/*/metadata.json")
        )
        noisy_library, _ = _noisy_chapters(library_globs, taxonomy)

    noisy_by_basename = {**noisy_library, **noisy_raw}

    if Path(wiki_dir).exists():
        from kb.frontmatter import parse as parse_frontmatter

        for article in sorted(Path(wiki_dir).rglob("*.md")):
            relative_parts = article.relative_to(wiki_dir).parts
            if any(part.startswith("_") for part in relative_parts):
                continue
            try:
                meta, _ = parse_frontmatter(article.read_text(encoding="utf-8"))
            except OSError:
                continue
            source = meta.get("source")
            if source in noisy_by_basename:
                books, chapter_title, category = noisy_by_basename[source]
                candidates.append(
                    NoiseCandidate(
                        path=article,
                        kind="article",
                        category=category,
                        book=" | ".join(books),
                        chapter_title=chapter_title,
                        summary=_summary_mirror(article, Path(wiki_dir)),
                    )
                )
                continue
            title = (meta.get("title") or "").strip().strip("'\"")
            title_category = classify_chapter(title, taxonomy) if title else None
            if title_category:
                candidates.append(
                    NoiseCandidate(
                        path=article,
                        kind="article",
                        category=title_category,
                        summary=_summary_mirror(article, Path(wiki_dir)),
                    )
                )
    return candidates

