import pytest


def test_archive_moves_orphans(tmp_path):
    # RED: falha até 006-kb-archive ser implementada
    from kb.archive import find_orphans

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "a.md").write_text("[[b]]")
    (wiki / "b.md").write_text("conteudo\n[[a]]")
    (wiki / "c.md").write_text("orfao")

    orphans = find_orphans(wiki)
    assert len(orphans) == 1
    assert orphans[0].name == "c.md"


def test_archive_older_than_filters_by_mtime(tmp_path):
    from kb.archive import find_by_age
    import os
    import time

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    old = wiki / "old.md"
    new = wiki / "new.md"
    old.write_text("x")
    new.write_text("y")

    ten_days_ago = time.time() - (10 * 86400)
    os.utime(old, (ten_days_ago, ten_days_ago))

    result = find_by_age(wiki, days=5)
    assert len(result) == 1
    assert result[0].name == "old.md"


def test_archive_dry_run_does_not_move_files(tmp_path):
    # RED: falha até 006-kb-archive ser implementada
    from kb.archive import move_to_archive

    wiki = tmp_path / "wiki"
    archive = tmp_path / "archive"
    wiki.mkdir()
    archive.mkdir()
    f = wiki / "topic" / "foo.md"
    f.parent.mkdir()
    f.write_text("x")

    candidates = [
        {"source": f, "reason": "orphan", "dest": archive / "topic" / "foo.md"}
    ]
    log = move_to_archive(candidates, archive, dry_run=True)
    assert f.exists()
    assert not (archive / "topic" / "foo.md").exists()
    assert len(log) == 1


def test_archive_preserves_directory_structure(tmp_path):
    # RED: falha até 006-kb-archive ser implementada
    from kb.archive import move_to_archive

    wiki = tmp_path / "wiki"
    archive = tmp_path / "archive"
    wiki.mkdir()
    archive.mkdir()
    f = wiki / "ai" / "foo.md"
    f.parent.mkdir()
    f.write_text("x")

    candidates = [{"source": f, "reason": "orphan", "dest": archive / "ai" / "foo.md"}]
    move_to_archive(candidates, archive, dry_run=False)
    assert not f.exists()
    assert (archive / "ai" / "foo.md").read_text() == "x"


def test_archive_stale_uses_threshold(tmp_path, monkeypatch):
    from kb.archive import collect_candidates
    import os
    import time

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    old = wiki / "old.md"
    new = wiki / "new.md"
    old.write_text("x")
    new.write_text("y")

    ten_days_ago = time.time() - (10 * 86400)
    os.utime(old, (ten_days_ago, ten_days_ago))
    monkeypatch.setattr("kb.archive.get_health_summary", lambda: {"stale_pct": 5.0})

    candidates = collect_candidates(wiki, stale=True)
    assert any(c["source"].name == "old.md" for c in candidates)
    assert not any(c["source"].name == "new.md" for c in candidates)


def test_archive_empty_wiki_raises_error(tmp_path):
    # RED: falha até 006-kb-archive ser implementada
    from kb.archive import collect_candidates

    wiki = tmp_path / "empty"
    with pytest.raises(ValueError):
        collect_candidates(wiki)


def test_archive_older_than_non_positive_raises_error(tmp_path):
    # RED: falha até 006-kb-archive ser implementada
    from kb.archive import collect_candidates

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    with pytest.raises(ValueError):
        collect_candidates(wiki, older_than=0)
