from unittest.mock import patch

from kb.jobs import list_jobs, run_job


def test_should_list_canonical_jobs():
    jobs = list_jobs()

    assert {job.name for job in jobs} == {"compile", "lint", "review"}



def test_should_run_jobs_via_underlying_modules(tmp_raw_wiki):
    with patch("kb.compile.discover_compile_targets") as mock_targets, patch("kb.compile.compile_file") as mock_compile, patch(
        "kb.compile.update_index"
    ) as mock_update_index, patch("kb.lint.lint_wiki") as mock_lint, patch("kb.heal.heal") as mock_heal:
        mock_targets.return_value = []
        mock_heal.return_value = []

        assert "compile" in run_job("compile")
        assert mock_compile.call_count == 0
        assert mock_update_index.called

        assert run_job("lint") == "Job lint executado."
        assert mock_lint.called

        assert "review" in run_job("review")
        assert mock_heal.called
