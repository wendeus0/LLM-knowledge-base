"""Índice lexical persistente do corpus da wiki (P2 de memory/next_steps.md).

Guarda por artigo o que o ranking lexical precisa — frequência de termo,
comprimento em tokens e hash de conteúdo — em kb_state/lexical.json. Mesmo
contrato do índice de embeddings: formato versionado, reconstrução incremental
por hash e degradação silenciosa. Sem índice utilizável a busca relê a wiki
inteira, exatamente como antes deste módulo existir.

O texto não entra no índice: o trecho de exibição sai da leitura sob demanda
dos poucos artigos devolvidos, não dos milhares que casaram o termo.
"""

import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

INDEX_FILENAME = "lexical.json"
INDEX_FORMAT = 1

_AUTO_REFRESH_OFF = ("0", "false", "off", "no")

# Corpus por (wiki_dir, state_dir) com a assinatura que o validou. Uma execução
# como `kb bench` dispara 152 queries: sem isto, 152 parses do mesmo JSON.
_cache: dict[tuple[str, str], tuple[dict, dict]] = {}


def tokenize(text):
    """Tokenização canônica do canal lexical: sequências `\\w` em minúsculas."""
    return re.findall(r"\w+", text.lower())


def _content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _iter_articles(wiki_dir):
    """(relpath, path) dos artigos da wiki, ignorando infra `_*` e ocultos `.*`."""
    for md in sorted(Path(wiki_dir).rglob("*.md")):
        relative = md.relative_to(wiki_dir)
        if any(part.startswith(("_", ".")) for part in relative.parts):
            continue
        yield str(relative), md


def _fingerprint(wiki_dir):
    """Assinatura barata do corpus: tamanho e mtime por artigo, sem ler conteúdo.

    O hash de conteúdo governa a reconstrução; o stat responde "mudou alguma
    coisa?" a cada query sem pagar a leitura que o índice existe para evitar.
    """
    signature = {}
    for relpath, md in _iter_articles(wiki_dir):
        try:
            info = md.stat()
        except OSError:
            continue
        signature[relpath] = [info.st_size, info.st_mtime_ns]
    return signature


def _entry_is_usable(entry):
    """Entrada com a forma que `_build_rankings` consome.

    JSON sintaticamente válido não garante estrutura: um índice truncado ou
    editado à mão passava no parse e estourava `KeyError` na busca — o oposto
    da promessa de que índice corrompido degrada para a leitura direta.
    """
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("length"), int)
        and isinstance(entry.get("tf"), dict)
        and isinstance(entry.get("size"), int)
        and isinstance(entry.get("mtime"), int)
    )


def _matches(docs, fingerprint):
    if set(docs) != set(fingerprint):
        return False
    return all(
        _entry_is_usable(entry)
        and [entry["size"], entry["mtime"]] == fingerprint[relpath]
        for relpath, entry in docs.items()
    )


def _read_docs(state_dir):
    """Entradas do índice em disco, ou None se ausente, ilegível ou de outra versão."""
    index_file = Path(state_dir) / INDEX_FILENAME
    if not index_file.exists():
        return None
    try:
        payload = json.loads(index_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("format") != INDEX_FORMAT:
        return None
    docs = payload.get("docs")
    return docs if isinstance(docs, dict) else None


def _read_stable(md, tentativas=3):
    """Texto e stat de um artigo que não mudou durante a leitura.

    Com o stat só depois da leitura, um arquivo reescrito no meio gravaria o
    conteúdo velho carregando o fingerprint novo — e a próxima query serviria
    dado obsoleto como fresco, sem nada que detectasse. Aqui o stat cerca a
    leitura; se divergir, relê. Instabilidade persistente devolve None, e o
    artigo entra na reconstrução seguinte.
    """
    for _ in range(tentativas):
        try:
            antes = md.stat()
            text = md.read_text(encoding="utf-8", errors="replace")
            depois = md.stat()
        except OSError:
            return None
        if (antes.st_size, antes.st_mtime_ns) == (depois.st_size, depois.st_mtime_ns):
            return text, depois
    return None


def _build_docs(wiki_dir, previous):
    docs = {}
    indexed = 0
    for relpath, md in _iter_articles(wiki_dir):
        leitura = _read_stable(md)
        if leitura is None:
            continue
        text, info = leitura
        digest = _content_hash(text)
        entry = previous.get(relpath)
        if entry and entry.get("hash") == digest:
            docs[relpath] = {**entry, "size": info.st_size, "mtime": info.st_mtime_ns}
            continue
        tokens = tokenize(text)
        docs[relpath] = {
            "hash": digest,
            "size": info.st_size,
            "mtime": info.st_mtime_ns,
            "length": len(tokens),
            "tf": dict(Counter(tokens)),
        }
        indexed += 1
    report = {
        "indexed": indexed,
        "unchanged": len(docs) - indexed,
        "removed": len([relpath for relpath in previous if relpath not in docs]),
        "total": len(docs),
    }
    return docs, report


def _write_docs(state_dir, docs):
    """Persiste o índice; falha de escrita vira aviso, nunca exceção no chamador."""
    from kb.fsutil import atomic_write_text

    payload = {"format": INDEX_FORMAT, "docs": docs}
    try:
        Path(state_dir).mkdir(parents=True, exist_ok=True)
        atomic_write_text(Path(state_dir) / INDEX_FILENAME, json.dumps(payload, ensure_ascii=False))
    except OSError as exc:
        print(f"aviso: índice lexical não gravado — {exc}", file=sys.stderr)


def _auto_refresh_enabled():
    """Mesma chave do índice semântico: a suíte desliga os dois de uma vez."""
    return os.getenv("KB_INDEX_AUTO_REFRESH", "1").strip().lower() not in _AUTO_REFRESH_OFF


def _remember(wiki_dir, state_dir, fingerprint, docs):
    _cache[(str(Path(wiki_dir)), str(Path(state_dir)))] = (fingerprint, docs)


def build_index(wiki_dir, state_dir, force=False):
    """(Re)constrói o índice lexical, reaproveitando entradas cujo hash não mudou."""
    previous = {} if force else (_read_docs(state_dir) or {})
    fingerprint = _fingerprint(wiki_dir)
    docs, report = _build_docs(wiki_dir, previous)
    _write_docs(state_dir, docs)
    _remember(wiki_dir, state_dir, fingerprint, docs)
    return report


def lexical_corpus(wiki_dir, state_dir):
    """Corpus indexado (`{relpath: {"length", "tf", ...}}`) ou None.

    None não é erro: é o sinal para o chamador reler a wiki. Acontece quando o
    índice está ausente, corrompido, de outra versão ou defasado com o
    auto-refresh desligado (`KB_INDEX_AUTO_REFRESH=0`).
    """
    fingerprint = _fingerprint(wiki_dir)
    cached = _cache.get((str(Path(wiki_dir)), str(Path(state_dir))))
    if cached and cached[0] == fingerprint:
        return cached[1]

    stored = _read_docs(state_dir)
    if stored is not None and _matches(stored, fingerprint):
        _remember(wiki_dir, state_dir, fingerprint, stored)
        return stored

    if not _auto_refresh_enabled():
        return None

    docs, _ = _build_docs(wiki_dir, stored or {})
    _write_docs(state_dir, docs)
    if set(docs) != set(fingerprint):
        # Artigo que não estabilizou na leitura, ou que apareceu/sumiu durante a
        # construção: servir este índice entregaria um corpus menor que a wiki e
        # o resultado divergiria do caminho sem índice. Relê desta vez.
        return None
    _remember(wiki_dir, state_dir, fingerprint, docs)
    return docs
