"""Contrato HTTP de disponibilidade da API local."""

from importlib import import_module

from fastapi.testclient import TestClient


def _client():
    try:
        app = import_module("kb.api.app").app
    except ModuleNotFoundError:
        app = None
    assert app is not None
    return TestClient(app)


def test_should_report_local_availability_without_paths():
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
