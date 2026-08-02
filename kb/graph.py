"""Traversal de wikilinks para enriquecer contexto de QA."""

import re
from pathlib import Path

from kb.frontmatter import parse


def extract_wikilinks(content: str) -> list[str]:
    """Extrai [[wikilinks]] únicos do conteúdo markdown."""
    found = re.findall(r"\[\[([^\]]+)\]\]", content)
    seen = []
    for link in found:
        if link not in seen:
            seen.append(link)
    return seen


def _slugify_link(link: str) -> str:
    return re.sub(r"\s+", "-", link.strip().lower())


def _e_artigo(path: Path, wiki_dir: Path) -> bool:
    """Derivados (`_summaries/`, `_sources/`, `_index.md`) não são artigos.

    Mesma convenção que `kb.search` já aplica ao indexar.
    """
    return not any(part.startswith(("_", ".")) for part in path.relative_to(wiki_dir).parts)


def build_link_index(wiki_dir: Path) -> dict:
    """Índice de resolução de wikilink, construído uma vez.

    Sem isto, resolver N links em M artigos custa N varreduras do disco — o
    vault de 1.040 artigos travou o lint na primeira execução real.
    """
    por_stem: dict[str, list[Path]] = {}
    por_slug: dict[str, Path] = {}
    for path in sorted(
        (p for p in wiki_dir.rglob("*.md") if not p.is_symlink() and _e_artigo(p, wiki_dir)),
        key=lambda p: p.relative_to(wiki_dir).as_posix(),
    ):
        por_stem.setdefault(path.stem.lower(), []).append(path)
        por_slug[path.relative_to(wiki_dir).with_suffix("").as_posix()] = path
    return {"por_stem": por_stem, "por_slug": por_slug}


def resolve_wikilink_all(link: str, wiki_dir: Path, index: dict | None = None) -> list[Path]:
    """Todos os artigos que um wikilink pode designar, em ordem estável.

    `[[topic/slug]]` designa exatamente um. `[[slug]]` designa todos os artigos
    com aquele stem — o vault tem 4 stems duplicados, e quem chama precisa
    saber disso em vez de receber um dos dois em ordem de sistema de arquivos.

    Passe `index` de `build_link_index` ao resolver muitos links seguidos.
    """
    idx = index or build_link_index(wiki_dir)
    alvo = _slugify_link(link)
    if "/" in alvo:
        achado = idx["por_slug"].get(alvo)
        return [achado] if achado else []
    return list(idx["por_stem"].get(alvo, []))


def resolve_wikilink(link: str, wiki_dir: Path, index: dict | None = None) -> Path | None:
    """Resolve um wikilink para o Path do arquivo em wiki/.

    Ambíguo devolve o primeiro em ordem estável — nunca em ordem de `rglob`,
    que o sistema de arquivos não garante e que fazia a mesma wiki resolver
    diferente entre execuções.
    """
    candidatos = resolve_wikilink_all(link, wiki_dir, index)
    return candidatos[0] if candidatos else None


def load_frontmatter(path: Path) -> dict:
    """Lê apenas o bloco YAML frontmatter de um arquivo markdown."""
    text = path.read_text(encoding="utf-8", errors="replace")
    meta, _ = parse(text)
    return meta


_STOP_WORDS = {"o", "a", "e", "é", "de", "do", "da", "em", "no", "na", "se", "com", "um", "uma", "os", "as", "ou"}


def _is_relevant(frontmatter: dict, question: str) -> bool:
    """Verifica se o frontmatter do arquivo é relevante para a pergunta."""
    stripped = re.sub(r"[^\w\s]", "", question.lower())
    terms = {t for t in stripped.split() if len(t) > 2 and t not in _STOP_WORDS}
    if not terms:
        return False
    title = frontmatter.get("title", "").lower()
    tags = [t.lower() for t in (frontmatter.get("tags") or [])]
    return any(term in title or any(term in tag for tag in tags) for term in terms)


def traverse(
    seed_files: list[Path],
    question: str,
    wiki_dir: Path,
    depth: int = 1,
    token_budget: int = 8000,
) -> list[Path]:
    """BFS sobre wikilinks a partir dos seed_files, respeitando budget e depth.

    Retorna lista de arquivos adicionais relevantes (não inclui seed_files).
    """
    visited = set(seed_files)
    result = []

    tokens_used = sum(len(p.read_text(encoding="utf-8", errors="replace")) // 4 for p in seed_files)

    queue = []
    for seed in seed_files:
        content = seed.read_text(encoding="utf-8", errors="replace")
        for link in extract_wikilinks(content):
            queue.append((link, 1))

    while queue and tokens_used < token_budget:
        link, current_depth = queue.pop(0)
        path = resolve_wikilink(link, wiki_dir)
        if path is None or path in visited:
            continue
        visited.add(path)

        fm = load_frontmatter(path)
        if not _is_relevant(fm, question):
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        tokens_used += len(content) // 4
        if tokens_used > token_budget:
            break

        result.append(path)

        if current_depth < depth:
            for nested_link in extract_wikilinks(content):
                queue.append((nested_link, current_depth + 1))

    return result
