"""Contrato do helper de git.

Reescrito quando `commit()` passou a resolver o repositório que contém o
arquivo, em vez de assumir `ROOT`. A versão anterior destes testes patcheava
`kb.git.ROOT` e verificava a ordem das chamadas ao subprocess — ou seja,
validava a mecânica do defeito: com `KB_DATA_DIR` fora do repo do código, o
commit era descartado em silêncio.

Comportamento observável (commit criado, arquivo rastreado, aviso emitido) é
verificado em `test_git_target_repo.py`, com repositórios reais. Aqui ficam os
casos de borda de execução.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch

from kb.git import _run, commit, repo_root_for


def _init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    return path


class TestRun:
    def test_should_execute_git_against_the_given_repo(self, tmp_path):
        with patch("kb.git.subprocess.run") as mock_run:
            _run(tmp_path, "status")

            mock_run.assert_called_once_with(
                ["git", "-C", str(tmp_path), "status"],
                check=True,
                capture_output=True,
            )

    def test_should_pass_multiple_arguments(self, tmp_path):
        with patch("kb.git.subprocess.run") as mock_run:
            _run(tmp_path, "add", "a.txt", "b.txt")

            mock_run.assert_called_once_with(
                ["git", "-C", str(tmp_path), "add", "a.txt", "b.txt"],
                check=True,
                capture_output=True,
            )


class TestRepoRootFor:
    def test_should_find_root_from_nested_file(self, tmp_path):
        vault = _init_repo(tmp_path / "vault")
        nested = vault / "wiki" / "ai" / "artigo.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("# A\n", encoding="utf-8")

        assert repo_root_for(nested).resolve() == vault.resolve()

    def test_should_return_none_outside_any_repo(self, tmp_path):
        orfao = tmp_path / "solto" / "artigo.md"
        orfao.parent.mkdir(parents=True)
        orfao.write_text("# A\n", encoding="utf-8")

        assert repo_root_for(orfao) is None


class TestCommitEdgeCases:
    def test_should_not_touch_git_when_disabled(self):
        with patch("kb.git.subprocess.run") as mock_run:
            commit("mensagem", [Path("qualquer.txt")], enabled=False)

            mock_run.assert_not_called()

    def test_should_warn_and_return_false_when_git_fails(self, tmp_path, capsys):
        vault = _init_repo(tmp_path / "vault")
        artigo = vault / "artigo.md"
        artigo.write_text("# A\n", encoding="utf-8")

        with patch(
            "kb.git._commit_in",
            side_effect=subprocess.CalledProcessError(1, "git", stderr=b"boom"),
        ):
            resultado = commit("mensagem", [artigo])

        assert resultado is False
        assert "boom" in capsys.readouterr().err

    def test_should_accept_empty_path_list(self):
        assert commit("mensagem", []) is True
