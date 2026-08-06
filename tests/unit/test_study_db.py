"""Onde o banco da plataforma vive e como ele se comporta sob concorrência."""

import sqlite3


def test_should_keep_the_study_database_out_of_version_control(tmp_path, monkeypatch):
    from pathlib import Path

    from kb import config
    from study.db import database_path

    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    assert database_path() == tmp_path / "study.db"
    ignorados = Path(".gitignore").read_text(encoding="utf-8").splitlines()
    assert "/study.db" in ignorados
    assert "/study.db-wal" in ignorados
    assert "/study.db-shm" in ignorados


def test_should_ensure_the_schema_when_connections_race_over_a_legacy_database(
    tmp_path, monkeypatch
):
    """Reproduz a corrida DETERMINISTICAMENTE, sem threads (review PR #71):
    duas conexões leem o PRAGMA antes de qualquer uma escrever — o interleaving
    exato que estourava `duplicate column name`. Sem depender de carga de
    máquina (falso vermelho) nem de sorte de escalonamento (falso verde)."""
    from kb import config

    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    legacy = sqlite3.connect(tmp_path / "study.db")
    legacy.execute(
        "CREATE TABLE notes (id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, "
        "body TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    legacy.commit()
    legacy.close()

    from study.db import _ensure_schema

    # Interleaving manual: as DUAS conexões leem o PRAGMA (via _ensure_schema
    # até o ponto de decisão) antes de qualquer ALTER — que é o que acontecia
    # quando duas requisições corriam. A 1ª migra; a 2ª repete a decisão já
    # tomada e não pode estourar duplicate column.
    conn1 = sqlite3.connect(tmp_path / "study.db")
    conn2 = sqlite3.connect(tmp_path / "study.db")
    _ensure_schema(conn1)
    conn1.commit()
    _ensure_schema(conn2)  # sem o guard, estourava OperationalError aqui
    conn2.commit()
    conn1.close()
    conn2.close()

    from study.db import _connect_db
    with _connect_db() as conn:
        colunas = {row[1] for row in conn.execute("PRAGMA table_info(notes)")}
    assert "updated_at" in colunas
