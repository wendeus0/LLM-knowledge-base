"""Traversal de wikilinks para enriquecer contexto de QA."""

import re
from pathlib import Path


def extract_wikilinks(content: str) -> list[str]:
    """Extrai [[wikilinks]] únicos do conteúdo markdown."""
    found = re.findall(r"\[\[([^\]]+)\]\]", content)
    seen = []
    for link in found:
        if link not in seen:
            seen.append(link)
    return seen


def resolve_wikilink(link: str, wiki_dir: Path) -> Path | None:
    """Resolve um wikilink para o Path do arquivo em wiki/."""
    slug = re.sub(r"\s+", "-", link.lower())
    for candidate in wiki_dir.rglob("*.md"):
        if candidate.stem == slug or candidate.stem == link:
            return candidate
    return None


def load_frontmatter(path: Path) -> dict:
    """Lê apenas o bloco YAML frontmatter de um arquivo markdown."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    yaml_block = text[3:end].strip()
    result = {}
    for line in yaml_block.splitlines():
        if ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip()
        value = raw_value.strip()
        # Parse lista simples [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
            result[key] = items
        else:
            result[key] = value
    return result


def _is_relevant(frontmatter: dict, question: str) -> bool:
    """Verifica se o frontmatter do arquivo é relevante para a pergunta."""
    terms = set(question.lower().split())
    title = frontmatter.get("title", "").lower()
    tags = [t.lower() for t in (frontmatter.get("tags") or [])]
    return any(term in title or term in tags for term in terms)


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
