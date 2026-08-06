"""Onde o banco da plataforma vive e como ele se comporta sob concorrência."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor


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
    from kb import config
    from study.db import _connect_db, _ensure_schema

    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    legacy = sqlite3.connect(tmp_path / "study.db")
    legacy.execute(
        "CREATE TABLE notes (id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, "
        "body TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    legacy.commit()
    legacy.close()

    # Sem Barrier de propósito: exigir 8 threads simultâneas tornou o teste
    # refém da carga da máquina (e um Barrier sem timeout chegou a pendurar a
    # suíte). A corrida natural do pool reproduziu o bug original em 2 de 3
    # rodadas — suficiente para o RED, e o fix o torna determinístico.

    def migrar():
        with _connect_db() as conn:
            _ensure_schema(conn)
            conn.commit()
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        resultados = [futuro.result() for futuro in [pool.submit(migrar) for _ in range(8)]]

    assert all(resultados)
    with _connect_db() as conn:
        colunas = {row[1] for row in conn.execute("PRAGMA table_info(notes)")}
    assert "updated_at" in colunas
