import re
import tomllib
from pathlib import Path

from kb import __version__

ROOT = Path(__file__).resolve().parents[2]


def test_should_load_dynamic_version_from_package_module():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["hatch"]["version"]["path"] == "kb/__init__.py"


def test_should_keep_package_version_aligned_with_latest_changelog_release():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(
        r"^##\s+\[([0-9]+\.[0-9]+\.[0-9]+)\]\s+-", changelog, re.MULTILINE
    )

    assert match is not None
    assert __version__ == match.group(1)
