"""Renderização segura de Markdown e wikilinks para o leitor."""

import re
from collections import defaultdict
from html import escape
from urllib.parse import quote, urlencode

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin


def _wikilink_rule(state, silent):
    if not state.src.startswith("[[", state.pos):
        return False
    end = state.src.find("]]", state.pos + 2)
    if end == -1:
        return False
    text = state.src[state.pos + 2 : end].strip()
    if not text or "\n" in text:
        return False
    if not silent:
        token = state.push("wikilink", "", 0)
        token.content = text
    state.pos = end + 2
    return True


def _wikilink_renderer(_renderer, _tokens, index, _options, env):
    token = _tokens[index]
    text = token.content
    occurrences = env["wikilinks_by_text"].get(text, [])
    position = env["wikilink_positions"][text]
    env["wikilink_positions"][text] += 1
    link = occurrences[position] if position < len(occurrences) else None
    escaped_text = escape(text)

    if link and link["ambiguous"]:
        marker = escape("ambíguo")
        return (
            '<a class="wikilink wikilink--ambiguous" href="#wikilink-ambiguous" '
            'aria-label="Wikilink ambíguo; escolha um destino no corpus">'
            f"{escaped_text} <span>{marker}</span></a>"
        )
    if link and len(link["targets"]) == 1:
        target = quote(link["targets"][0], safe="/")
        return f'<a class="wikilink" href="/a/{target}">{escaped_text}</a>'

    source_id = env["missing_wikilinks"]
    env["missing_wikilinks"] += 1
    query = urlencode({"termo": text})
    return (
        f'<button class="wikilink wikilink--missing" type="button" '
        f'hx-get="/fontes?{query}" hx-target="#fontes-{source_id}" hx-swap="innerHTML" '
        f'title="Sem artigo ainda — clique para buscar fontes deste tema" '
        f'aria-label="{escaped_text}: sem artigo; buscar fontes deste tema">{escaped_text}</button>'
        f'<span class="sources-result" id="fontes-{source_id}"></span>'
    )


def _sem_titulo_repetido(content: str) -> str:
    """Descarta o `# título` inicial, que o template já mostra do frontmatter."""
    linhas = content.lstrip("\n").split("\n")
    if linhas and linhas[0].startswith("# "):
        return "\n".join(linhas[1:]).lstrip("\n")
    return content


def render_markdown(
    content: str, wikilinks: list[dict], highlights: list[dict] | None = None
) -> str:
    """Converte Markdown em HTML usando os destinos resolvidos pela API."""
    renderer = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    renderer.use(tasklists_plugin)
    renderer.inline.ruler.before("emphasis", "wikilink", _wikilink_rule)
    renderer.add_render_rule("wikilink", _wikilink_renderer)
    by_text = defaultdict(list)
    for link in wikilinks:
        by_text[link["text"]].append(link)
    html = renderer.render(
        _sem_titulo_repetido(content),
        {
            "wikilinks_by_text": by_text,
            "wikilink_positions": defaultdict(int),
            "missing_wikilinks": 0,
        },
    )
    return _apply_highlights(html, highlights or [])


def _apply_highlights(html: str, highlights: list[dict]) -> str:
    parts = re.split(r"(<[^>]+>)", html)
    for highlight in highlights:
        quote = escape(highlight["quote"])
        if not quote:
            continue
        marker = f'<mark class="highlight">{quote}</mark>'
        for index in range(0, len(parts), 2):
            if quote in parts[index]:
                parts[index] = parts[index].replace(quote, marker, 1)
                break
    return "".join(parts)
