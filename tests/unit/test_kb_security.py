from fastapi import FastAPI
from fastapi.testclient import TestClient


def _guarded_app():
    from kb.security import (
        loopback_only_middleware,
        reject_cross_origin_writes_middleware,
    )

    app = FastAPI()
    app.middleware("http")(reject_cross_origin_writes_middleware)
    app.middleware("http")(loopback_only_middleware)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.post("/mutate")
    def mutate():
        return {"ok": True}

    return app


def _client(host="127.0.0.1"):
    return TestClient(_guarded_app(), client=(host, 51234))


def test_should_allow_get_from_loopback_client():
    response = _client("127.0.0.1").get("/ping")

    assert response.status_code == 200


def test_should_reject_request_from_non_loopback_client():
    response = _client("203.0.113.5").get("/ping")

    assert response.status_code == 403


def test_should_allow_non_loopback_client_when_remote_access_env_is_set(monkeypatch):
    monkeypatch.setenv("KB_ALLOW_REMOTE_ACCESS", "1")

    response = _client("203.0.113.5").get("/ping")

    assert response.status_code == 200


def test_should_reject_write_when_origin_header_mismatches():
    response = _client().post(
        "/mutate", headers={"origin": "https://attacker.example"}
    )

    assert response.status_code == 403


def test_should_allow_write_when_origin_header_matches_request_host():
    client = _client()
    response = client.post("/mutate", headers={"origin": str(client.base_url).rstrip("/")})

    assert response.status_code == 200


def test_should_allow_write_when_referer_header_matches_and_origin_is_absent():
    client = _client()
    response = client.post(
        "/mutate", headers={"referer": f"{client.base_url}/a/some/article"}
    )

    assert response.status_code == 200


def test_should_reject_write_when_referer_header_mismatches_and_origin_is_absent():
    response = _client().post(
        "/mutate", headers={"referer": "https://attacker.example/evil"}
    )

    assert response.status_code == 403


def test_should_allow_write_when_both_origin_and_referer_are_absent():
    response = _client().post("/mutate")

    assert response.status_code == 200


def test_should_not_check_origin_for_get_requests():
    client = _client()
    response = client.get("/ping", headers={"origin": "https://attacker.example"})

    assert response.status_code == 200
