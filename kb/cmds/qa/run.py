"""Execução do comando qa desacoplada da CLI."""

from __future__ import annotations


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
    grounding_enabled: bool = True,
):
    traverse = not no_traverse

    if file_back:
        from kb.qa import answer_and_file

        args = {
            "allow_sensitive": allow_sensitive,
            "no_commit": no_commit,
            "to_wiki": to_wiki,
            "traverse": traverse,
            "depth": depth,
            "profile": profile,
            "top_k": top_k,
            "index_refresh_enabled": index_refresh_enabled,
            "rerank_depth": rerank_depth,
        }
        if not grounding_enabled:
            args["grounding_enabled"] = False
        response, saved_path = answer_and_file(question, **args)
    else:
        from kb.qa import answer

        args = {
            "allow_sensitive": allow_sensitive,
            "traverse": traverse,
            "depth": depth,
            "profile": profile,
            "top_k": top_k,
            "rerank_depth": rerank_depth,
        }
        if not grounding_enabled:
            args["grounding_enabled"] = False
        response = answer(question, **args)
        saved_path = None

    from kb import grounding
    from kb.qa import QaResult

    return QaResult(
        answer=response,
        grounding=getattr(response, "grounding", grounding.GroundingResult()),
        saved_path=saved_path,
    )
