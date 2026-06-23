def test_health_check(client) -> None:
    """
    Validates that GET /api/v1/health returns HTTP 200 and a status of 'ok'.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
