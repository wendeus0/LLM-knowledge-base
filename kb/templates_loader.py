"""Carregamento de templates markdown da engine ou do vault."""

import importlib.resources

import kb.config as _config


def resolve_template(name):
    """Resolve um template markdown, priorizando override local do vault."""
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(f"Nome de template inválido: {name}")

    vault_template = _config.DATA_DIR / "templates" / f"{name}.md"
    if vault_template.is_file():
        return vault_template.read_text(encoding="utf-8")

    engine_template = importlib.resources.files("kb") / "templates" / f"{name}.md"
    if engine_template.is_file():
        return engine_template.read_text(encoding="utf-8")

    raise FileNotFoundError(f"Template '{name}' não encontrado no vault nem na engine")
