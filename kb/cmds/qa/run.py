"""Execução do comando qa desacoplada da CLI."""

from __future__ import annotations

from pathlib import Path


def execute_qa_command(
    *,
    question: str,
    file_back: bool,
    to_wiki: bool,
    allow_sensitive: bool,
    no_commit: bool,
    no_traverse: bool,
    depth: int,
    profile: str = "fast",
    top_k: int | None = None,
    index_refresh_enabled: bool = True,
    rerank_depth: int | None = None,
) -> tuple[str, Path | None]:
    traverse = not no_traverse

    if file_back:
        from kb.qa import answer_and_file

        return answer_and_file(
            question,
            allow_sensitive=allow_sensitive,
            no_commit=no_commit,
            to_wiki=to_wiki,
            traverse=traverse,
            depth=depth,
            profile=profile,
            top_k=top_k,
            index_refresh_enabled=index_refresh_enabled,
            rerank_depth=rerank_depth,
        )

    from kb.qa import answer

    response = answer(
        question,
        allow_sensitive=allow_sensitive,
        traverse=traverse,
        depth=depth,
        profile=profile,
        top_k=top_k,
        rerank_depth=rerank_depth,
    )
    return response, None
