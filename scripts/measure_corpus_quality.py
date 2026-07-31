#!/usr/bin/env python3
"""Mede o corpus de um vault sem escrever nele.

Uso: python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section all
"""

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


TEMPLATE_SECTIONS = (
    "Contexto e motivação",
    "Conceitos centrais",
    "Como funciona",
    "Exemplos",
    "Limitações e trade-offs",
    "Conceitos Relacionados",
    "Referências",
)
EXCLUDED_DIRECTORIES = {"_summaries", "_sources", "_outputs", "_pipeline", "_docs"}
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[[^\]\n]+\]\]")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$", re.MULTILINE)


def parse_frontmatter(text):
    """Lê o frontmatter YAML plano usado pelos artigos sem depender do pacote kb."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        return {}, text
    meta = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, "".join(lines[end + 1 :])


def normalise_heading(value):
    return " ".join(value.strip().casefold().split())


SECTION_KEYS = {normalise_heading(name): name for name in TEMPLATE_SECTIONS}


def count_words(text):
    return len(WORD_RE.findall(text))


def percentile(values, fraction):
    """Percentil com interpolação linear, equivalente à definição padrão de planilhas."""
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return values[low]
    return values[low] + (values[high] - values[low]) * (position - low)


def distribution(values):
    return {
        "min": min(values),
        "p10": percentile(values, 0.10),
        "p25": percentile(values, 0.25),
        "median": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": max(values),
    }


def formatted_distribution(values, digits=1):
    data = distribution(values)
    return " ".join(
        f"{key}={value:.{digits}f}" if isinstance(value, float) else f"{key}={value}"
        for key, value in data.items()
    )


def article_paths(wiki_dir):
    """Retorna os arquivos que kb.embeddings._iter_articles indexaria."""
    paths = []
    for path in sorted(wiki_dir.rglob("*.md")):
        relative = path.relative_to(wiki_dir)
        if any(part.startswith(("_", ".")) for part in relative.parts):
            continue
        paths.append(path)
    return paths


def section_blocks(body):
    matches = list(HEADING_RE.finditer(body))
    blocks = defaultdict(list)
    for index, match in enumerate(matches):
        heading = SECTION_KEYS.get(normalise_heading(match.group(1)))
        if heading is None:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end() : end]
        blocks[heading].append(content)
    return blocks


def has_meaningful_content(text):
    without_rules = re.sub(r"(?m)^\s*---\s*$", "", text)
    without_note = re.sub(r"(?m)^\s*>\s*\*\*Nota:\*\*.*$", "", without_rules)
    return bool(without_note.strip())


def reference_items(blocks):
    items = []
    for block in blocks.get("Referências", []):
        items.extend(item.strip() for item in LIST_ITEM_RE.findall(block))
    return items


def is_candidate_bibliographic_reference(item):
    """Proxy verificável: item de lista não é wikilink nem placeholder de template."""
    return "[[" not in item and "]]" not in item and "<" not in item and ">" not in item


def collect_articles(vault):
    wiki_dir = vault / "wiki"
    articles = []
    for path in article_paths(wiki_dir):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(text)
        blocks = section_blocks(body)
        refs = reference_items(blocks)
        sections = sum(
            1
            for section in TEMPLATE_SECTIONS
            if any(has_meaningful_content(block) for block in blocks.get(section, []))
        )
        articles.append(
            {
                "path": path.relative_to(wiki_dir).as_posix(),
                "absolute_path": path,
                "body": body,
                "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "topic": meta.get("topic", ""),
                "source": meta.get("source", ""),
                "words": count_words(body),
                "chars": len(body),
                "sections": sections,
                "wikilinks": len(WIKILINK_RE.findall(body)),
                "references": len(refs),
                "candidate_bibliographic_references": sum(
                    is_candidate_bibliographic_reference(item) for item in refs
                ),
            }
        )
    return articles


def source_candidates(vault):
    """Indexa cópias locais de fonte que podem ser pareadas pelo valor de `source`."""
    roots = (vault / "raw", vault / "library", vault / "wiki" / "_sources")
    by_relative = defaultdict(list)
    by_basename = defaultdict(list)
    counts = {}
    for root in roots:
        root_count = 0
        if not root.exists():
            counts[str(root.relative_to(vault))] = 0
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".txt", ".rst"}:
                continue
            root_count += 1
            candidate = (root, path)
            by_relative[path.relative_to(root).as_posix()].append(candidate)
            by_basename[path.name].append(candidate)
        counts[str(root.relative_to(vault))] = root_count
    return by_relative, by_basename, counts


def read_source_word_count(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    _, body = parse_frontmatter(text)
    return count_words(body), hashlib.sha256(text.encode("utf-8")).hexdigest()


def compression_measurement(articles, vault):
    by_relative, by_basename, source_counts = source_candidates(vault)
    cache = {}
    paired = []
    unresolved = 0
    ambiguous = 0
    by_method = Counter()
    examples = []
    for article in articles:
        source = article["source"].replace("\\", "/").lstrip("./")
        candidates = by_relative.get(source, [])
        method = "relative-path"
        if not candidates:
            candidates = by_basename.get(Path(source).name, [])
            method = "unique-basename"
        if not candidates:
            unresolved += 1
            continue
        described = []
        for root, path in candidates:
            if path not in cache:
                cache[path] = read_source_word_count(path)
            words, digest = cache[path]
            described.append((root, path, words, digest))
        digests = {item[3] for item in described}
        if len(described) > 1 and len(digests) > 1:
            ambiguous += 1
            continue
        root, path, input_words, _ = described[0]
        ratio = input_words / article["words"] if article["words"] else None
        if ratio is None:
            unresolved += 1
            continue
        paired.append({"article": article["path"], "source_path": str(path), "input_words": input_words, "output_words": article["words"], "ratio": ratio})
        if len(described) > 1:
            method = "identical-content-basename"
        by_method[method] += 1
    paired.sort(key=lambda item: (item["ratio"], item["article"]))
    return {
        "source_candidates": source_counts,
        "paired": paired,
        "unresolved": unresolved,
        "ambiguous": ambiguous,
        "methods": by_method,
    }


def normalised_article_vectors(index_path, expected_hashes):
    with index_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    articles = payload.get("articles", {})
    actual_paths = set(articles)
    expected_paths = set(expected_hashes)
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or extra:
        raise ValueError(f"embeddings.json não coincide com wiki: missing={missing[:3]} extra={extra[:3]}")
    stale = sorted(path for path, digest in expected_hashes.items() if articles[path].get("hash") != digest)
    if stale:
        raise ValueError(f"embeddings.json contém vetores stale: {stale[:3]}")
    vectors = []
    for path in sorted(expected_paths):
        chunks = articles[path].get("chunks", [])
        if not chunks:
            raise ValueError(f"{path}: sem chunks no índice")
        aggregate = None
        valid_chunks = 0
        for chunk in chunks:
            vector = chunk.get("vector")
            if not vector:
                continue
            if aggregate is None:
                aggregate = [0.0] * len(vector)
            if len(vector) != len(aggregate):
                raise ValueError(f"{path}: dimensão inconsistente")
            for index, value in enumerate(vector):
                aggregate[index] += value
            valid_chunks += 1
        if not valid_chunks:
            raise ValueError(f"{path}: nenhum chunk vetorizado")
        aggregate = [value / valid_chunks for value in aggregate]
        norm = math.sqrt(sum(value * value for value in aggregate))
        if not norm:
            raise ValueError(f"{path}: vetor agregado nulo")
        vectors.append((path, [value / norm for value in aggregate], valid_chunks))
    return payload, vectors


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def duplicate_measurement(articles, vault):
    expected_hashes = {article["path"]: article["text_hash"] for article in articles}
    payload, vectors = normalised_article_vectors(vault / "kb_state" / "embeddings.json", expected_hashes)
    maxima = [(-2.0, None) for _ in vectors]
    pairs = []
    for left_index, (left_path, left_vector, _) in enumerate(vectors):
        for right_index in range(left_index + 1, len(vectors)):
            right_path, right_vector, _ = vectors[right_index]
            similarity = dot(left_vector, right_vector)
            pairs.append((similarity, left_path, right_path))
            if similarity > maxima[left_index][0]:
                maxima[left_index] = (similarity, right_path)
            if similarity > maxima[right_index][0]:
                maxima[right_index] = (similarity, left_path)
    pairs.sort(key=lambda item: (-item[0], item[1], item[2]))
    return {
        "format": payload.get("format"),
        "model": payload.get("model"),
        "dimension": payload.get("dim"),
        "index_articles": len(payload.get("articles", {})),
        "chunks": sum(chunks for _, _, chunks in vectors),
        "maxima": [item[0] for item in maxima],
        "pairs": pairs,
    }


def print_universe(articles, vault):
    explicit = [
        path
        for path in (vault / "wiki").rglob("*.md")
        if not any(part in EXCLUDED_DIRECTORIES for part in path.relative_to(vault / "wiki").parts)
    ]
    print(f"articles_indexable={len(articles)}")
    print(f"markdown_after_named_directory_exclusions={len(explicit)}")
    print("extra_excluded_by_indexer=" + ",".join(
        sorted(path.relative_to(vault / "wiki").as_posix() for path in explicit if path not in {a['absolute_path'] for a in articles})
    ))


def print_size(articles):
    words = [article["words"] for article in articles]
    chars = [article["chars"] for article in articles]
    print("words " + formatted_distribution(words))
    print("chars " + formatted_distribution(chars))
    for threshold in (50, 100, 150):
        print(f"words_at_most_{threshold}={sum(value <= threshold for value in words)}")
    print("smallest_20")
    for article in sorted(articles, key=lambda item: (item["words"], item["chars"], item["path"]))[:20]:
        print(f"{article['words']}\t{article['chars']}\t{article['path']}")


def print_structure(articles):
    for label, key in (("template_sections_nonempty", "sections"), ("reference_items", "references"), ("candidate_bibliographic_reference_items", "candidate_bibliographic_references")):
        values = [article[key] for article in articles]
        frequencies = Counter(values)
        print(f"{label} distribution={formatted_distribution(values)} frequencies=" + ",".join(f"{value}:{frequencies[value]}" for value in sorted(frequencies)))
    print("wikilinks distribution=" + formatted_distribution([article["wikilinks"] for article in articles]))
    print("articles_with_at_least_5_candidate_bibliographic_references=" + str(sum(article["candidate_bibliographic_references"] >= 5 for article in articles)))


def print_compression(articles, vault):
    result = compression_measurement(articles, vault)
    paired = result["paired"]
    print("source_candidates=" + ",".join(f"{name}:{count}" for name, count in sorted(result["source_candidates"].items())))
    total = len(articles)
    print(
        f"paired_articles={len(paired)} paired_rate={len(paired) / total:.3f} "
        f"unresolved_articles={result['unresolved']} unresolved_rate={result['unresolved'] / total:.3f} "
        f"ambiguous_articles={result['ambiguous']} ambiguous_rate={result['ambiguous'] / total:.3f}"
    )
    print("pairing_methods=" + ",".join(f"{name}:{count}" for name, count in sorted(result["methods"].items())))
    if paired:
        print("input_words " + formatted_distribution([item["input_words"] for item in paired]))
        print("output_words " + formatted_distribution([item["output_words"] for item in paired]))
        print("input_to_output_ratio " + formatted_distribution([item["ratio"] for item in paired], 2))
        print("pairing_examples")
        for item in paired[:5]:
            print(f"{item['ratio']:.2f}\t{item['input_words']}\t{item['output_words']}\t{item['article']}\t{item['source_path']}")


def examples_for_band(pairs, lower, upper=None):
    selected = [pair for pair in pairs if pair[0] >= lower and (upper is None or pair[0] < upper)]
    return selected[:3]


def print_duplicates(articles, vault):
    result = duplicate_measurement(articles, vault)
    pairs = result["pairs"]
    print(f"index format={result['format']} model={result['model']} dimension={result['dimension']} articles={result['index_articles']} chunks={result['chunks']}")
    print("maximum_similarity_per_article " + formatted_distribution(result["maxima"], 4))
    for threshold in (0.95, 0.90, 0.85):
        print(f"pairs_at_or_above_{threshold:.2f}={sum(pair[0] >= threshold for pair in pairs)}")
    for label, lower, upper in (("gte_0.95", 0.95, None), ("0.90_to_0.95", 0.90, 0.95), ("0.85_to_0.90", 0.85, 0.90)):
        examples = examples_for_band(pairs, lower, upper)
        print(f"examples_{label}={len(examples)}")
        for similarity, left, right in examples:
            print(f"{similarity:.6f}\t{left}\t{right}")


def print_topics(articles):
    global_p25 = percentile([article["words"] for article in articles], 0.25)
    grouped = defaultdict(list)
    for article in articles:
        grouped[article["topic"] or "<missing>"].append(article)
    print(f"global_word_p25={global_p25:.1f}")
    print("topic\tarticles\tmedian_words\tshort_at_or_below_global_p25\tshort_rate")
    for topic, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        short = sum(article["words"] <= global_p25 for article in group)
        print(f"{topic}\t{len(group)}\t{percentile([article['words'] for article in group], 0.5):.1f}\t{short}\t{short / len(group):.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument(
        "--section",
        choices=("all", "universe", "size", "structure", "compression", "duplicates", "topics"),
        default="all",
    )
    args = parser.parse_args()
    vault = args.vault.resolve()
    articles = collect_articles(vault)
    if args.section in {"all", "universe"}:
        print_universe(articles, vault)
    if args.section in {"all", "size"}:
        print_size(articles)
    if args.section in {"all", "structure"}:
        print_structure(articles)
    if args.section in {"all", "compression"}:
        print_compression(articles, vault)
    if args.section in {"all", "duplicates"}:
        print_duplicates(articles, vault)
    if args.section in {"all", "topics"}:
        print_topics(articles)


if __name__ == "__main__":
    main()
