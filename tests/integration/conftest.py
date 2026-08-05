import pytest


@pytest.fixture
def api_client():
    """Cliente da API com host loopback — `loopback_only_middleware` recusa o resto.

    O import fica dentro da fixture: `fastapi` é extra opcional, e importá-lo no
    topo do conftest quebraria a coleta da suíte inteira em vez de pular.
    """
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from kb.api.app import app

    return TestClient(app, client=("127.0.0.1", 51234))
