"""Health checks LLM sobre a wiki."""

import re
from pathlib import Path

from kb.client import chat
from kb.config import WIKI_DIR
from kb.guardrails import assert_safe_for_provider
from kb.sampling import params

SYSTEM = """Você é um auditor de knowledge base. Analise os artigos fornecidos e identifique:
1. Inconsistências ou informações contraditórias entre artigos
2. Dados ausentes ou incompletos
3. Wikilinks quebrados (referências a artigos que não existem)
4. Oportunidades de novos artigos (conceitos mencionados mas não desenvolvidos)
5. Sugestões de perguntas interessantes para aprofundar o tema

Formato de saída em markdown com seções para cada categoria.
"""


def find_ambiguous_wikilinks(wiki_dir: Path) -> list[str]:
    """Wikilinks que designam mais de um artigo.

    O link `[[honeycomb]]` não diz qual honeycomb; o vault tem 4 stems
    duplicados. Qualificar por topic (`[[cybersecurity/honeycomb]]`) resolve, e
    é isso que este check pede ao autor.
    """
    from kb.graph import build_link_index, resolve_wikilink_all

    index = build_link_index(wiki_dir)
    achados: list[str] = []
    for md in sorted(wiki_dir.rglob("*.md"), key=lambda p: p.as_posix()):
        if md.is_symlink():
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        vistos: set[str] = set()
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            chave = link.strip().lower()
            if chave in vistos:
                continue
            vistos.add(chave)
            candidatos = resolve_wikilink_all(link, wiki_dir, index)
            if len(candidatos) > 1:
                alvos = ", ".join(
                    c.relative_to(wiki_dir).with_suffix("").as_posix() for c in candidatos
                )
                achados.append(f"  - `{md.name}` → [[{link}]] designa {len(candidatos)}: {alvos}")
    return achados


def lint_wiki(allow_sensitive: bool = False) -> str:
    articles = list(WIKI_DIR.rglob("*.md"))
    if not articles:
        return "Wiki vazia. Use `kb compile` para adicionar artigos."

    existing_names = {p.stem.lower() for p in articles}

    # Detecta wikilinks quebrados localmente (sem LLM)
    broken: list[str] = []
    for md in articles:
        text = md.read_text(encoding="utf-8", errors="replace")
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            slug = link.lower().replace(" ", "-")
            if slug not in existing_names and link.lower() not in existing_names:
                broken.append(f"  - `{md.name}` → [[{link}]]")

    context = "\n\n---\n\n".join(
        f"# {p.stem}\n{p.read_text(encoding='utf-8')}" for p in articles[:20]
    )

    assert_safe_for_provider(context, source="lint:wiki", allow_sensitive=allow_sensitive)

    response = chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Artigos da wiki:\n\n{context}"},
        ],
        # Auditoria: relatar o que existe, não imaginar problemas.
        **params("analytical"),
    )

    ambiguos = find_ambiguous_wikilinks(WIKI_DIR)

    if broken:
        broken_section = "\n## Wikilinks Quebrados (detectados localmente)\n\n" + "\n".join(broken)
        response += broken_section
    if ambiguos:
        response += (
            "\n\n## Wikilinks Ambíguos (designam mais de um artigo)\n\n"
            + "\n".join(ambiguos)
            + "\n\nQualifique por topic: `[[cybersecurity/honeycomb]]`."
        )

    return response
