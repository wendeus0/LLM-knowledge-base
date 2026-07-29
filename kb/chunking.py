"""Divisão de artigo em chunks por seção (feature 017-chunking-por-secao).

Um vetor por artigo dilui: um texto de 20 mil caracteres reduzido a uma média
não representa bem nenhum dos assuntos que cobre, e o que passa de 8k nem é
lido. A wiki já traz a estrutura pronta — todos os artigos têm headings `##`,
com seções de mediana 647 caracteres.
"""

import re

_HEADING_RE = re.compile(r"^## +(.+?)\s*$", re.M)
_FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)


def strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1)


def split_sections(text: str) -> list[tuple[str, str]]:
    """Corpo em (heading, conteúdo). Preâmbulo vira seção de heading vazio.

    Headings mais profundos (`###`) permanecem dentro da seção `##` que os
    contém — são subdivisões de um mesmo assunto, não assuntos novos.
    """
    body = strip_frontmatter(text)
    matches = list(_HEADING_RE.finditer(body))

    if not matches:
        return [("", body.strip())]

    sections: list[tuple[str, str]] = []
    preamble = body[: matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections.append((match.group(1).strip(), body[start:end].strip()))

    return sections


def _merge_short(sections: list[tuple[str, str]], min_chars: int) -> list[tuple[str, str]]:
    """Seção curta demais vira vetor de ruído — junta com a seguinte."""
    merged: list[tuple[str, str]] = []
    pending_heading: str | None = None
    pending_body: list[str] = []

    for heading, body in sections:
        if pending_body:
            pending_body.append(f"{heading}\n{body}" if heading else body)
            if sum(len(part) for part in pending_body) >= min_chars:
                merged.append((pending_heading or "", "\n\n".join(pending_body)))
                pending_heading, pending_body = None, []
            continue

        if len(body) < min_chars:
            pending_heading, pending_body = heading, [body]
        else:
            merged.append((heading, body))

    if pending_body:
        merged.append((pending_heading or "", "\n\n".join(pending_body)))

    return merged


def _split_on_boundary(body: str, budget: int) -> list[str]:
    """Divide sem cortar palavra ao meio, preferindo quebra de linha."""
    pieces: list[str] = []
    remaining = body

    while len(remaining) > budget:
        window = remaining[:budget]
        cut = window.rfind("\n")
        if cut < budget // 2:
            cut = window.rfind(" ")
        if cut < budget // 2:
            cut = budget
        pieces.append(remaining[:cut])
        remaining = remaining[cut:].lstrip()

    pieces.append(remaining)
    return pieces


def build_chunks(
    title: str, text: str, max_chars: int = 8000, min_chars: int = 200
) -> list[dict]:
    """Chunks prontos para embedar, cada um carregando o contexto do artigo.

    Sem o título e o heading no texto, uma seção "Gotchas" isolada não diz de
    que assunto trata.
    """
    chunks: list[dict] = []

    for heading, body in _merge_short(split_sections(text), min_chars):
        prefix = f"{title} — {heading}\n" if heading else f"{title}\n"
        budget = max_chars - len(prefix)
        if budget <= 0:
            budget = max_chars

        for piece in _split_on_boundary(body, budget):
            chunks.append({"heading": heading, "text": prefix + piece})

    return chunks
