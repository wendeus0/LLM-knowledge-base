"""Classificação e limpeza de capítulos-ruído do corpus (feature 011-corpus-noise-filter).

Ruído = capítulo sem conteúdo de conhecimento: agradecimentos, dedicatória,
prefácio, elogios, encerramento (epílogo/posfácio), colofão, sobre o autor,
copyright, índice remissivo. Conclusão/Considerações finais são conteúdo e
nunca entram na taxonomia default (decisão do dono, 2026-07-15).
"""

import json
import shutil
import tomllib
import unicodedata
from pathlib import Path

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


def scan_corpus(
    raw_dir: Path, wiki_dir: Path, taxonomy: dict[str, list[str]] | None = None
) -> list[Path]:
    """Lista candidatos a ruído já ingeridos: capítulos em raw/books/ e artigos wiki derivados."""
    if taxonomy is None:
        taxonomy = load_taxonomy()
    candidates: list[Path] = []
    noisy_chapter_files: set[str] = set()
    for metadata_path in sorted(Path(raw_dir).glob("books/*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for chapter in metadata.get("chapters", []):
            category = classify_chapter(chapter.get("title") or "", taxonomy)
            if not category:
                continue
            chapter_file = chapter.get("file")
            if not chapter_file:
                continue
            chapter_path = _chapter_path_inside_book(metadata_path, chapter_file)
            if chapter_path is None:
                continue
            noisy_chapter_files.add(chapter_file)
            if chapter_path.exists():
                candidates.append(chapter_path)
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
            if meta.get("source") in noisy_chapter_files:
                candidates.append(article)
                continue
            title = (meta.get("title") or "").strip().strip("'\"")
            if title and classify_chapter(title, taxonomy):
                candidates.append(article)
    return candidates


def archive_candidates(candidates: list[Path], archive_dir: Path) -> list[Path]:
    """Move candidatos para archive/ (nunca deleta); conflito de nome ganha sufixo."""
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []
    for source in candidates:
        destination = archive_dir / source.name
        suffix = 1
        while destination.exists():
            destination = archive_dir / f"{source.stem}-{suffix}{source.suffix}"
            suffix += 1
        shutil.move(str(source), str(destination))
        moved.append(destination)
    return moved
