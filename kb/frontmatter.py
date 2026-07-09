def has_frontmatter(text):
    """Retorna se o texto tem bloco de frontmatter YAML fechado."""
    meta, body = parse(text)
    return bool(meta) or body != text


LIST_KEYS = {"tags"}


def parse(text):
    """Extrai frontmatter YAML plano e corpo de um documento markdown.

    Colchetes viram lista apenas nas chaves de LIST_KEYS; nas demais o valor
    é preservado como string literal (evita quebrar consumidores de title/topic).
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = None
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text

    meta = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in LIST_KEYS and value.startswith("[") and value.endswith("]"):
            meta[key] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        else:
            meta[key] = value

    return meta, "".join(lines[end_index + 1 :])


def serialize(meta, body):
    """Serializa metadados YAML planos e corpo em documento markdown."""
    lines = []
    for key, value in meta.items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value)
            lines.append(f"{key}: [{rendered}]")
        else:
            lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body
