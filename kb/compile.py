"""Compila documentos de raw/ para a wiki em markdown."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import re
import unicodedata
from pathlib import Path
from kb.client import chat, is_provider_resource_limit_error
from kb.config import RAW_DIR, WIKI_DIR, TOPICS
from kb.git import commit
from kb.guardrails import assert_safe_for_provider
from kb.state import (
    extract_summary,
    find_compiled_entry,
    mark_compiled,
    upsert_knowledge,
)

SYSTEM = """Você é um compilador de knowledge base. Dado um documento bruto (geralmente em inglês), você:
1. Identifica o tópico principal (cybersecurity, ai, python, typescript, ou geral)
2. Extrai e organiza os conceitos-chave
3. Gera um artigo wiki em PORTUGUÊS em markdown com frontmatter YAML, seções claras e wikilinks [[conceito]]
4. O artigo deve ser auto-contido mas referenciar outros conceitos relacionados com [[wikilinks]]
5. Termos técnicos consolidados (ex: LLM, transformer, gradient descent) podem permanecer em inglês

Formato de saída — apenas o markdown bruto, sem explicações e SEM code fences envolvendo o output:

---
title: <título em português>
topic: <topic>
tags: [tag1, tag2]
source: <nome do arquivo original>
translated_by: ai
---

# <título>

<conteúdo em português>

## Conceitos Relacionados
- [[conceito1]]
- [[conceito2]]

---
> **Nota:** Este artigo foi gerado e traduzido automaticamente por IA a partir de material em inglês. Pode conter imprecisões. Consulte a fonte original para informações definitivas.
"""


def _strip_outer_fence(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip() + "\n"


TEXT_SOURCE_EXTENSIONS = {".md", ".markdown", ".txt", ".rst"}
IGNORED_RAW_FILENAMES = {"metadata.json"}
NOISE_PATTERNS = [
    r"^draft \([^\)]*\) of .*feedback: .*",
    r"^this material is published by cambridge university press.*$",
    r"^c⃝.*published by cambridge university press.*$",
    r"^c\(\) ?\d{4}.*$",
]


@dataclass(frozen=True)
class CompileArtifact:
    raw_path: Path
    source_name: str
    compiled_markdown: str
    topic: str
    title: str
    summary_text: str


@dataclass(frozen=True)
class CompileFailure:
    raw_path: Path
    error: Exception


@dataclass(frozen=True)
class CompileBatchResult:
    outputs: list[Path]
    failures: list[CompileFailure]


def _read_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _resolve_raw_path(raw_path: Path) -> Path:
    return raw_path if raw_path.is_absolute() else RAW_DIR / raw_path


def _prepare_prompt_content(text: str, aggressive: bool = False) -> str:
    normalized = (
        unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    )
    cleaned_lines = []

    for line in normalized.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()

        if any(re.match(pattern, lowered) for pattern in NOISE_PATTERNS):
            continue

        if aggressive and stripped.startswith("<") and stripped.endswith(">"):
            continue

        cleaned_lines.append(line.rstrip())

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _build_prompt(raw_path: Path, content: str, aggressive: bool = False) -> str:
    label = "Documento pré-processado" if aggressive else "Documento"
    return f"{label}: {raw_path.name}\n\n{_prepare_prompt_content(content, aggressive=aggressive)}"


def _is_compile_target(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() in TEXT_SOURCE_EXTENSIONS
        and path.name not in IGNORED_RAW_FILENAMES
    )


def find_book_dirs(name: str) -> list[Path]:
    from kb.book_import_core import slugify

    books_dir = RAW_DIR / "books"
    if not books_dir.exists():
        return []
    needle = slugify(name)
    return [d for d in books_dir.iterdir() if d.is_dir() and needle in d.name]


def discover_compile_targets(base: Path | None = None) -> list[Path]:
    root = base or RAW_DIR
    if root.is_file():
        return [root] if _is_compile_target(root) else []
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if _is_compile_target(path))


def _wiki_path(topic: str, title: str) -> Path:
    from kb.book_import_core import slugify

    slug = slugify(title)[:60]
    folder = WIKI_DIR / topic if topic in TOPICS else WIKI_DIR
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{slug}.md"


def _resolve_output_path(raw_path: Path, topic: str, title: str) -> Path:
    existing_entry = find_compiled_entry(raw_path)
    if existing_entry:
        existing_article = existing_entry.get("article")
        if existing_article:
            article_path = Path(existing_article)
            article_path.parent.mkdir(parents=True, exist_ok=True)
            return article_path
    return _wiki_path(topic, title)


def _summary_path(article_path: Path) -> Path:
    summaries_dir = WIKI_DIR / "summaries"
    relative_parent = article_path.parent.relative_to(WIKI_DIR)
    target_dir = summaries_dir / relative_parent
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / article_path.name


def _extract_topic_and_title(
    compiled_markdown: str, fallback_title: str
) -> tuple[str, str]:
    topic = "general"
    title = fallback_title
    for line in compiled_markdown.splitlines():
        if line.startswith("topic:"):
            candidate = line.split(":", 1)[1].strip()
            if candidate in TOPICS:
                topic = candidate
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()
    return topic, title


def _write_summary(
    article_path: Path,
    topic: str,
    title: str,
    source_name: str,
    compiled_markdown: str,
    summary_text: str | None = None,
) -> Path:
    summary_path = _summary_path(article_path)
    summary_text = summary_text or extract_summary(compiled_markdown)
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


def compile_to_artifact(
    raw_path: Path, allow_sensitive: bool = False
) -> CompileArtifact:
    raw_path = _resolve_raw_path(raw_path)
    content = _read_raw(raw_path)
    assert_safe_for_provider(
        content, source=f"compile:{raw_path.name}", allow_sensitive=allow_sensitive
    )

    try:
        response = chat(
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": _build_prompt(raw_path, content)},
            ]
        )
    except Exception as exc:
        if not is_provider_resource_limit_error(exc):
            raise

        response = chat(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM
                    + "\n\nO texto de entrada foi pré-processado para remover ruído de paginação/OCR. "
                    "Se houver lacunas, preserve apenas o conteúdo semanticamente útil.",
                },
                {
                    "role": "user",
                    "content": _build_prompt(raw_path, content, aggressive=True),
                },
            ]
        )

    compiled_markdown = _strip_outer_fence(response)
    topic, title = _extract_topic_and_title(compiled_markdown, raw_path.stem)
    return CompileArtifact(
        raw_path=raw_path,
        source_name=raw_path.name,
        compiled_markdown=compiled_markdown,
        topic=topic,
        title=title,
        summary_text=extract_summary(compiled_markdown),
    )


def persist_artifact(artifact: CompileArtifact, no_commit: bool = True) -> Path:
    out = _resolve_output_path(artifact.raw_path, artifact.topic, artifact.title)
    out.write_text(artifact.compiled_markdown, encoding="utf-8")
    summary_path = _write_summary(
        out,
        artifact.topic,
        artifact.title,
        artifact.source_name,
        artifact.compiled_markdown,
        summary_text=artifact.summary_text,
    )

    mark_compiled(artifact.raw_path, out, summary_path, artifact.topic, artifact.title)
    upsert_knowledge(
        {
            "title": artifact.title,
            "topic": artifact.topic,
            "source": str(artifact.raw_path),
            "article": str(out),
            "summary": str(summary_path),
            "summary_text": artifact.summary_text,
        }
    )

    if not no_commit:
        commit(
            f"feat(wiki): compile {artifact.source_name} → {out.name}",
            [out, summary_path],
        )
    return out


def compile_file(
    raw_path: Path, allow_sensitive: bool = False, no_commit: bool = True
) -> Path:
    artifact = compile_to_artifact(raw_path, allow_sensitive=allow_sensitive)
    return persist_artifact(artifact, no_commit=no_commit)


def compile_many(
    targets: list[Path],
    workers: int = 4,
    allow_sensitive: bool = False,
    no_commit: bool = True,
    update_index_enabled: bool = True,
) -> CompileBatchResult:
    ordered_targets = [_resolve_raw_path(target) for target in targets]
    if not ordered_targets:
        return CompileBatchResult(outputs=[], failures=[])

    artifacts_by_index: dict[int, CompileArtifact] = {}
    failures_by_index: dict[int, CompileFailure] = {}
    effective_workers = max(1, min(workers, len(ordered_targets)))

    if effective_workers == 1:
        for index, raw_path in enumerate(ordered_targets):
            try:
                artifacts_by_index[index] = compile_to_artifact(
                    raw_path, allow_sensitive=allow_sensitive
                )
            except Exception as exc:
                failures_by_index[index] = CompileFailure(raw_path=raw_path, error=exc)
    else:
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            futures = {
                executor.submit(
                    compile_to_artifact, raw_path, allow_sensitive=allow_sensitive
                ): (index, raw_path)
                for index, raw_path in enumerate(ordered_targets)
            }
            for future in as_completed(futures):
                index, raw_path = futures[future]
                try:
                    artifacts_by_index[index] = future.result()
                except Exception as exc:
                    failures_by_index[index] = CompileFailure(
                        raw_path=raw_path, error=exc
                    )

    outputs = []
    for index in range(len(ordered_targets)):
        artifact = artifacts_by_index.get(index)
        if artifact is None:
            continue
        outputs.append(persist_artifact(artifact, no_commit=no_commit))

    if outputs and update_index_enabled:
        update_index(no_commit=no_commit)

    failures = [failures_by_index[index] for index in sorted(failures_by_index)]
    return CompileBatchResult(outputs=outputs, failures=failures)


def update_index(no_commit: bool = True) -> None:
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
