"""RED — `--commit` tem de versionar o repo que contém o arquivo.

`kb/git.py` resolvia tudo contra `ROOT` (o repositório do código). Com
`KB_DATA_DIR` apontando para um vault fora do repo — que é exatamente o setup
recomendado pelo `.env.example` — `relative_to(ROOT)` levantava ValueError, o
path era descartado e `commit()` retornava True sem fazer nada.

Resultado: `kb compile --commit` nunca versionou o vault, em silêncio.
"""

import subprocess

from kb.git import commit, is_git_repo


def _init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    return path


def _log_count(path):
    result = subprocess.run(
        ["git", "-C", str(path), "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
    )
    return int(result.stdout.strip()) if result.returncode == 0 else 0


class TestCommitOutsideCodeRepo:
    def test_should_commit_into_the_repo_that_contains_the_file(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")
        artigo = vault / "wiki" / "artigo.md"
        artigo.parent.mkdir(parents=True)
        artigo.write_text("# Artigo\n", encoding="utf-8")

        assert commit("feat: artigo novo", [artigo]) is True
        assert _log_count(vault) == 1

    def test_should_include_the_file_in_the_commit(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")
        artigo = vault / "wiki" / "artigo.md"
        artigo.parent.mkdir(parents=True)
        artigo.write_text("# Artigo\n", encoding="utf-8")

        commit("feat: artigo novo", [artigo])

        tracked = subprocess.run(
            ["git", "-C", str(vault), "ls-files"], capture_output=True, text=True
        ).stdout
        assert "wiki/artigo.md" in tracked

    def test_should_warn_instead_of_silently_succeeding_when_no_repo(
        self, tmp_path, capsys
    ):
        orfao = tmp_path / "sem-repo" / "artigo.md"
        orfao.parent.mkdir(parents=True)
        orfao.write_text("# Artigo\n", encoding="utf-8")

        resultado = commit("feat: artigo", [orfao])

        assert resultado is False
        assert "reposit" in capsys.readouterr().err.lower()

    def test_should_group_paths_by_repo(self, tmp_path):
        vault_a = _init_repo(tmp_path / "a")
        vault_b = _init_repo(tmp_path / "b")
        file_a = vault_a / "x.md"
        file_b = vault_b / "y.md"
        file_a.write_text("a\n", encoding="utf-8")
        file_b.write_text("b\n", encoding="utf-8")

        commit("feat: dois vaults", [file_a, file_b])

        assert _log_count(vault_a) == 1
        assert _log_count(vault_b) == 1

    def test_should_respect_enabled_false(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")
        artigo = vault / "artigo.md"
        artigo.write_text("# A\n", encoding="utf-8")

        assert commit("feat: nao deve commitar", [artigo], enabled=False) is True
        assert _log_count(vault) == 0

    def test_is_git_repo_should_detect_arbitrary_path(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")

        assert is_git_repo(vault) is True
        assert is_git_repo(tmp_path / "sem-repo") is False


class TestNoChanges:
    def test_should_not_create_empty_commit(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")
        artigo = vault / "artigo.md"
        artigo.write_text("# A\n", encoding="utf-8")
        commit("feat: primeiro", [artigo])

        commit("feat: sem mudanca", [artigo])

        assert _log_count(vault) == 1
