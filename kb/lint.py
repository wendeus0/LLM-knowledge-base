"""Health checks LLM sobre a wiki."""

import re

from kb.client import chat
from kb.config import WIKI_DIR


SYSTEM = """Você é um auditor de knowledge base. Analise os artigos fornecidos e identifique:
1. Inconsistências ou informações contraditórias entre artigos
2. Dados ausentes ou incompletos
3. Wikilinks quebrados (referências a artigos que não existem)
4. Oportunidades de novos artigos (conceitos mencionados mas não desenvolvidos)
5. Sugestões de perguntas interessantes para aprofundar o tema

Formato de saída em markdown com seções para cada categoria.
"""


def lint_wiki() -> str:
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

    response = chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Artigos da wiki:\n\n{context}"},
        ]
    )

    if broken:
        broken_section = "\n## Wikilinks Quebrados (detectados localmente)\n\n" + "\n".join(broken)
        response += broken_section

    return response
