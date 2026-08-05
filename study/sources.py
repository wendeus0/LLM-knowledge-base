"""Busca local e somente leitura de fontes para temas ainda sem artigo."""

import re
from pathlib import Path

_TEXT_EXTENSIONS = {
    ".csv",
    ".html",
    ".htm",
    ".json",
    ".markdown",
    ".md",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
}
_ORIGINS = (
    ("raw", "raw", "Compilar diretamente", "Material bruto pode virar artigo agora."),
    ("library", "library", "Importar livro antes", "EPUB e PDF exigem import-book antes."),
    (
        "sources",
        "wiki/_sources",
        "Procurar artigo existente",
        "O tema provavelmente já tem cobertura sob outro título.",
    ),
)


def _data_dir() -> Path:
    """Vault do usuário, resolvido pelo `kb`.

    `KB_DATA_DIR` vive no `.env`, que o `kb` carrega no import. Ler `os.getenv`
    cru aqui caía em `Path.cwd()` — o repositório, sem `raw/` — e o gancho de
    fontes não achava nada em produção nenhuma.
    """
    from kb import config

    return config.DATA_DIR


def _diretorio(origin: str, relative_root: str, root: Path, configurado: bool) -> Path:
    """Onde procurar cada origem.

    `KB_RAW_DIR` e `KB_WIKI_DIR` podem apontar para fora de `KB_DATA_DIR`;
    montar o caminho por concatenação ignorava a configuração e não achava nada.
    """
    if not configurado:
        return root / relative_root
    from kb import config

    if origin == "raw":
        return config.RAW_DIR
    if origin == "sources":
        return config.WIKI_DIR / "_sources"
    return root / relative_root


def _exibivel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _normalized(value: str) -> str:
    return re.sub(r"[^\w]+", " ", value.casefold()).strip()


def _matches(path: Path, term: str) -> bool:
    needle = _normalized(term)
    if not needle:
        return False
    if needle in _normalized(path.name):
        return True
    if path.suffix.casefold() not in _TEXT_EXTENSIONS:
        return False
    try:
        return needle in _normalized(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False


def buscar_fontes(termo: str, data_dir: Path | None = None) -> dict:
    """Encontra menções locais por origem, sem iniciar compilação ou provider."""
    root = data_dir or _data_dir()
    origins = []
    for origin, relative_root, action, message in _ORIGINS:
        directory = _diretorio(origin, relative_root, root, data_dir is None)
        matches = []
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.is_file() and not path.is_symlink() and _matches(path, termo):
                    matches.append({"path": _exibivel(path, root), "name": path.name})
        origins.append(
            {
                "origin": origin,
                "action": action,
                "message": message,
                "matches": sorted(matches, key=lambda item: item["path"]),
            }
        )
    return {"term": termo, "found": any(item["matches"] for item in origins), "origins": origins}
