"""Contrato HTTP de disponibilidade da API local."""

def test_should_report_local_availability_without_paths(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
