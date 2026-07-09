from kb.fsutil import atomic_write_text


def test_should_write_content_correctly(tmp_path):
    path = tmp_path / "article.md"

    atomic_write_text(path, "conteúdo\n")

    assert path.read_text(encoding="utf-8") == "conteúdo\n"


def test_should_leave_no_tmp_file_after_success(tmp_path):
    path = tmp_path / "article.md"

    atomic_write_text(path, "conteúdo\n")

    assert list(tmp_path.glob("*.tmp")) == []


def test_should_create_missing_parent_directory(tmp_path):
    path = tmp_path / "wiki" / "general" / "article.md"

    atomic_write_text(path, "conteúdo\n")

    assert path.read_text(encoding="utf-8") == "conteúdo\n"


def test_should_overwrite_previous_content_on_second_write(tmp_path):
    path = tmp_path / "article.md"

    atomic_write_text(path, "primeiro\n")
    atomic_write_text(path, "segundo\n")

    assert path.read_text(encoding="utf-8") == "segundo\n"
