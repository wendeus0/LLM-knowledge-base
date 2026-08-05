"""Renderização segura de Markdown e wikilinks para o leitor."""

import re
from collections import defaultdict
from html import escape, unescape
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
    # A API devolve uma entrada por texto distinto: a segunda ocorrência do
    # mesmo wikilink reusa o destino já resolvido em vez de virar "sem artigo".
    link = occurrences[min(position, len(occurrences) - 1)] if occurrences else None
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


def _build_renderer() -> MarkdownIt:
    renderer = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    renderer.use(tasklists_plugin)
    renderer.inline.ruler.before("emphasis", "wikilink", _wikilink_rule)
    renderer.add_render_rule("wikilink", _wikilink_renderer)
    return renderer


# O renderer não guarda estado entre chamadas — tudo o que varia vive no `env`.
_RENDERER = _build_renderer()
_TAG = re.compile(r"(<[^>]+>)")


def _to_html(content: str, wikilinks: list[dict]) -> str:
    by_text = defaultdict(list)
    for link in wikilinks:
        by_text[link["text"].strip()].append(link)
    return _RENDERER.render(
        _sem_titulo_repetido(content),
        {
            "wikilinks_by_text": by_text,
            "wikilink_positions": defaultdict(int),
            "missing_wikilinks": 0,
        },
    )


def plain_text(content: str, wikilinks: list[dict]) -> str:
    """Texto que o leitor enxerga — é contra ele que a seleção do browser casa.

    O destaque é selecionado na tela, não no Markdown: procurar a âncora no
    fonte cru orfanava todo destaque que passasse por ênfase, link ou wikilink.
    """
    return "".join(unescape(parte) for parte in _TAG.split(_to_html(content, wikilinks))[::2])


def render_markdown(
    content: str, wikilinks: list[dict], highlights: list[dict] | None = None
) -> str:
    """Converte Markdown em HTML usando os destinos resolvidos pela API."""
    return _apply_highlights(_to_html(content, wikilinks), highlights or [])


def _escapado(texto: str) -> str:
    """Escapa como o markdown-it: entidades para `& < > "`, apóstrofo intacto."""
    return escape(texto, quote=False).replace('"', "&quot;")


def _intervalos(textos: list[str], highlights: list[dict]) -> list[tuple[int, int]]:
    corrido = "".join(textos)
    encontrados = []
    for highlight in highlights:
        trecho = highlight.get("quote") or ""
        if not trecho:
            continue
        inicio = highlight.get("start")
        if inicio is None:
            inicio = corrido.find(trecho)
        if inicio is None or inicio < 0 or corrido[inicio : inicio + len(trecho)] != trecho:
            continue
        encontrados.append((inicio, inicio + len(trecho)))
    unidos: list[tuple[int, int]] = []
    for inicio, fim in sorted(encontrados):
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1] = (unidos[-1][0], max(unidos[-1][1], fim))
        else:
            unidos.append((inicio, fim))
    return unidos


def _apply_highlights(html: str, highlights: list[dict]) -> str:
    partes = _TAG.split(html)
    textos = [unescape(parte) for parte in partes[::2]]
    intervalos = _intervalos(textos, highlights)
    if not intervalos:
        return html
    saida = []
    posicao = 0
    for indice, parte in enumerate(partes):
        if indice % 2:
            saida.append(parte)
            continue
        texto = textos[indice // 2]
        saida.append(_marcar(texto, posicao, intervalos))
        posicao += len(texto)
    return "".join(saida)


def _marcar(texto: str, deslocamento: int, intervalos: list[tuple[int, int]]) -> str:
    """Marca a parte de cada intervalo que cai neste nó de texto.

    Um destaque que atravessa `**ênfase**` ocupa três nós; marcar só onde a
    string inteira aparece deixava esse destaque invisível.
    """
    locais = [
        (max(inicio - deslocamento, 0), min(fim - deslocamento, len(texto)))
        for inicio, fim in intervalos
        if inicio - deslocamento < len(texto) and fim - deslocamento > 0
    ]
    if not locais:
        return _escapado(texto)
    pedacos = []
    cursor = 0
    for inicio, fim in locais:
        pedacos.append(_escapado(texto[cursor:inicio]))
        pedacos.append(f'<mark class="highlight">{_escapado(texto[inicio:fim])}</mark>')
        cursor = fim
    pedacos.append(_escapado(texto[cursor:]))
    return "".join(pedacos)
