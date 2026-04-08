import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from kb.git import commit, _run


class TestRun:
    def test_should_execute_git_command_with_correct_arguments(self):
        with patch("kb.git.subprocess.run") as mock_run:
            _run("status")
            mock_run.assert_called_once_with(
                ["git", "-C", str(Path.cwd()), "status"],
                check=True,
                capture_output=True,
            )

    def test_should_pass_multiple_arguments_to_git(self):
        with patch("kb.git.subprocess.run") as mock_run:
            _run("add", "file1.txt", "file2.txt")
            mock_run.assert_called_once_with(
                ["git", "-C", str(Path.cwd()), "add", "file1.txt", "file2.txt"],
                check=True,
                capture_output=True,
            )


class TestCommit:
    def test_should_skip_commit_when_disabled(self):
        with patch("kb.git.subprocess.run") as mock_run:
            commit("message", [Path("test.txt")], enabled=False)
            mock_run.assert_not_called()

    def test_should_stage_and_commit_when_changes_exist(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("kb.git.ROOT", tmp_path):
            with patch("kb.git.subprocess.run") as mock_run:
                # First call (add) succeeds
                # Second call (diff --cached) returns exit code 1 (changes exist)
                # Third call (commit) succeeds
                mock_run.side_effect = [
                    Mock(returncode=0),  # add
                    Mock(returncode=1),  # diff --cached (has changes)
                    Mock(returncode=0),  # commit
                ]

                commit("feat: test", [test_file], enabled=True)

                assert mock_run.call_count == 3
                # Verify add was called with correct args
                assert mock_run.call_args_list[0][0][0] == [
                    "git",
                    "-C",
                    str(tmp_path),
                    "add",
                    "test.txt",
                ]
                # Verify commit was called
                assert mock_run.call_args_list[2][0][0] == [
                    "git",
                    "-C",
                    str(tmp_path),
                    "commit",
                    "-m",
                    "feat: test",
                ]

    def test_should_not_commit_when_no_changes_staged(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("kb.git.ROOT", tmp_path):
            with patch("kb.git.subprocess.run") as mock_run:
                # First call (add) succeeds
                # Second call (diff --cached) returns exit code 0 (no changes)
                mock_run.side_effect = [
                    Mock(returncode=0),  # add
                    Mock(returncode=0),  # diff --cached (no changes)
                ]

                commit("feat: test", [test_file], enabled=True)

                assert mock_run.call_count == 2
                # Verify commit was NOT called
                assert mock_run.call_args_list[1][0][0] == [
                    "git",
                    "-C",
                    str(tmp_path),
                    "diff",
                    "--cached",
                    "--quiet",
                ]

    def test_should_handle_called_process_error_gracefully(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("kb.git.ROOT", tmp_path):
            with patch("kb.git.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "git")

                # Should not raise
                commit("feat: test", [test_file], enabled=True)

    def test_should_handle_multiple_paths(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        with patch("kb.git.ROOT", tmp_path):
            with patch("kb.git.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    Mock(returncode=0),  # add
                    Mock(returncode=1),  # diff --cached (has changes)
                    Mock(returncode=0),  # commit
                ]

                commit("feat: test", [file1, file2], enabled=True)

                # Verify add was called with both files
                assert mock_run.call_args_list[0][0][0] == [
                    "git",
                    "-C",
                    str(tmp_path),
                    "add",
                    "file1.txt",
                    "file2.txt",
                ]

    def test_should_use_relative_paths(self, tmp_path):
        # Create a file in a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("content")

        with patch("kb.git.ROOT", tmp_path):
            with patch("kb.git.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    Mock(returncode=0),
                    Mock(returncode=1),
                    Mock(returncode=0),
                ]

                commit("feat: test", [test_file], enabled=True)

                # Verify relative path is used
                assert "subdir/test.txt" in mock_run.call_args_list[0][0][0]
