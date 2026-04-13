from kb.handoff import create_handoff


def test_create_handoff_should_write_structured_file(tmp_path, monkeypatch):
    monkeypatch.setattr("kb.handoff.DATA_DIR", tmp_path)

    path = create_handoff(
        scope="finalizar fase 3",
        summary="jobs e gate",
        branch="feat/test",
        next_steps="abrir pr",
        evidence="pytest -q",
        decisions="adotar OOF adaptado",
    )

    assert path.exists()
    assert path.parent == (tmp_path / "docs" / "handoffs")

    content = path.read_text(encoding="utf-8")
    assert "# Handoff de Sessão" in content
    assert "Escopo da sessão: finalizar fase 3" in content
    assert "Branch: feat/test" in content
    assert "jobs e gate" in content


def test_create_handoff_should_not_overwrite_when_called_twice_same_minute(
    tmp_path, monkeypatch
):
    monkeypatch.setattr("kb.handoff.DATA_DIR", tmp_path)
    monkeypatch.setattr("kb.handoff._timestamp", lambda: "2026-04-13-0100")

    first = create_handoff(scope="sessao 1")
    second = create_handoff(scope="sessao 2")

    assert first != second
    assert first.exists()
    assert second.exists()

    handoff_files = sorted((tmp_path / "docs" / "handoffs").glob("*.md"))
    assert len(handoff_files) == 2
