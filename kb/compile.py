"""Compila documentos de raw/ para a wiki em markdown."""

from pathlib import Path
from kb.client import chat
from kb.config import RAW_DIR, WIKI_DIR, TOPICS
from kb.git import commit
from kb.guardrails import assert_safe_for_provider
from kb.state import extract_summary, mark_compiled, upsert_knowledge


SYSTEM = """Você é um compilador de knowledge base. Dado um documento bruto, você:
1. Identifica o tópico principal (cybersecurity, ai, python, typescript, ou geral)
2. Extrai conceitos-chave
3. Gera um artigo wiki em markdown com frontmatter YAML, seções claras e wikilinks [[conceito]]
4. O artigo deve ser auto-contido mas referenciar outros conceitos relacionados com [[wikilinks]]

Formato de saída — apenas o markdown, sem explicações:
```
---
title: <título>
topic: <topic>
tags: [tag1, tag2]
source: <nome do arquivo original>
---

# <título>

<conteúdo>

## Conceitos Relacionados
- [[conceito1]]
- [[conceito2]]
```
"""


TEXT_SOURCE_EXTENSIONS = {".md", ".markdown", ".txt", ".rst"}
IGNORED_RAW_FILENAMES = {"metadata.json"}


def _read_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _is_compile_target(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in TEXT_SOURCE_EXTENSIONS and path.name not in IGNORED_RAW_FILENAMES


def discover_compile_targets(base: Path | None = None) -> list[Path]:
    root = base or RAW_DIR
    if root.is_file():
        return [root] if _is_compile_target(root) else []
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if _is_compile_target(path))


def _wiki_path(topic: str, title: str) -> Path:
    slug = title.lower().replace(" ", "-").replace("/", "-")[:60]
    folder = WIKI_DIR / topic if topic in TOPICS else WIKI_DIR
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{slug}.md"


def _summary_path(article_path: Path) -> Path:
    summaries_dir = WIKI_DIR / "summaries"
    relative_parent = article_path.parent.relative_to(WIKI_DIR)
    target_dir = summaries_dir / relative_parent
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / article_path.name


def _write_summary(article_path: Path, topic: str, title: str, source_name: str, compiled_markdown: str) -> Path:
    summary_path = _summary_path(article_path)
    summary_text = extract_summary(compiled_markdown)
    summary_path.write_text(
        (
            f"---\n"
            f"title: Summary — {title}\n"
            f"topic: {topic}\n"
            f"source: {source_name}\n"
            f"article: {article_path.relative_to(WIKI_DIR)}\n"
            f"---\n\n"
            f"# Summary — {title}\n\n"
            f"{summary_text}\n"
        ),
        encoding="utf-8",
    )
    return summary_path


def compile_file(raw_path: Path, allow_sensitive: bool = False, no_commit: bool = False) -> Path:
    content = _read_raw(raw_path)
    assert_safe_for_provider(content, source=f"compile:{raw_path.name}", allow_sensitive=allow_sensitive)
    prompt = f"Documento: {raw_path.name}\n\n{content}"

    response = chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ]
    )

    # Extrai frontmatter para determinar topic e title
    topic = "general"
    title = raw_path.stem
    for line in response.splitlines():
        if line.startswith("topic:"):
            t = line.split(":", 1)[1].strip()
            if t in TOPICS:
                topic = t
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()

    out = _wiki_path(topic, title)
    out.write_text(response, encoding="utf-8")
    summary_path = _write_summary(out, topic, title, raw_path.name, response)

    mark_compiled(raw_path, out, summary_path, topic, title)
    upsert_knowledge(
        {
            "title": title,
            "topic": topic,
            "source": str(raw_path),
            "article": str(out),
            "summary": str(summary_path),
            "summary_text": extract_summary(response),
        }
    )

    if not no_commit:
        commit(f"feat(wiki): compile {raw_path.name} → {out.name}", [out, summary_path])
    return out


def update_index(no_commit: bool = False) -> None:
    """Regenera _index.md listando todos os artigos da wiki."""
    articles: list[str] = []
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if md.name == "_index.md" or "summaries" in md.parts:
            continue
        rel = md.relative_to(WIKI_DIR)
        articles.append(f"- [[{md.stem}]] (`{rel}`)")

    index = WIKI_DIR / "_index.md"
    index.write_text(
        "---\ntitle: Index\n---\n\n# Knowledge Base Index\n\n"
        + "\n".join(articles)
        + "\n",
        encoding="utf-8",
    )
    if not no_commit:
        commit("chore(wiki): update _index.md", [index])
