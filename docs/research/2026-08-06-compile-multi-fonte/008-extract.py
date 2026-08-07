import json, re, collections
from pathlib import Path

VAULT = Path("/Users/wendeus/vault")
WIKI = VAULT / "wiki"
MANIFEST = VAULT / "kb_state" / "manifest.json"
ROOTS = [VAULT / "library", WIKI / "_sources", VAULT / "raw"]
OUT = Path(__file__).with_name("008-data.json")

def fm(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    head, body = text[3:end], text[end + 4:]
    d = {}
    for line in head.splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            d[m.group(1)] = m.group(2).strip()
    return d, body.lstrip("\n")

by_basename = collections.defaultdict(list)
total_sources = 0
for root in ROOTS:
    if not root.is_dir():
        continue
    for p in root.rglob("*.md"):
        if p.is_symlink():
            continue
        total_sources += 1
        by_basename[p.name].append(str(p.relative_to(VAULT)))

hist = collections.Counter(len(v) for v in by_basename.values())
collisions = {
    "total_sources": total_sources,
    "distinct_basenames": len(by_basename),
    "unique_basenames": sum(1 for v in by_basename.values() if len(v) == 1),
    "colliding_basenames": sum(1 for v in by_basename.values() if len(v) > 1),
    "collision_histogram": {str(k): v for k, v in sorted(hist.items()) if k > 1},
    "top_collisions": [
        {"basename": b, "count": len(v), "paths": v[:8]}
        for b, v in sorted(by_basename.items(), key=lambda kv: -len(kv[1]))[:20]
    ],
}

man = json.load(open(MANIFEST))
basename_entries = sorted(
    (e for e in man if e.get("provenance") == "backfill-basename"),
    key=lambda e: e.get("article") or "",
)
step = max(1, len(basename_entries) // 40)
sample_raw = basename_entries[::step][:40]

def head_of(path, n=1200):
    try:
        _, body = fm(path.read_text(errors="ignore"))
        return body[:n]
    except OSError:
        return None

sample = []
for e in sample_raw:
    art_rel = e.get("article") or ""
    art_path = WIKI / art_rel
    meta, body = ({}, "")
    if art_path.is_file():
        meta, body = fm(art_path.read_text(errors="ignore"))
    src_name = Path(e.get("source") or "").name
    found = by_basename.get(src_name, [])
    sample.append({
        "article": art_rel,
        "article_exists": art_path.is_file(),
        "article_title": meta.get("title"),
        "article_declared_source": meta.get("source"),
        "article_head": body[:1200],
        "manifest_source": e.get("source"),
        "manifest_book": e.get("book"),
        "source_paths_found": found,
        "source_head": head_of(VAULT / found[0]) if found else None,
    })

live = []
for p in WIKI.rglob("*.md"):
    rel = p.relative_to(WIKI)
    if p.is_symlink() or any(x.startswith(("_", ".")) for x in rel.parts):
        continue
    live.append(rel)
in_manifest = {e.get("article") for e in man if e.get("article")}

unresolved = []
for rel in sorted(live):
    if str(rel) in in_manifest:
        continue
    meta, _ = fm((WIKI / rel).read_text(errors="ignore"))
    src_name = Path(meta.get("source") or "").name
    unresolved.append({
        "article": str(rel),
        "title": meta.get("title"),
        "topic": meta.get("topic"),
        "declared_source": meta.get("source"),
        "source_paths_found": by_basename.get(src_name, []) if src_name else [],
        "at_wiki_root": len(rel.parts) == 1,
    })

data = {
    "collisions": collisions,
    "sample_basename": sample,
    "unresolved": unresolved,
    "counts": {
        "manifest_entries": len(man),
        "live_articles": len(live),
        "unresolved": len(unresolved),
        "by_provenance": dict(collections.Counter(e.get("provenance") for e in man)),
    },
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
print("OK", data["counts"])
