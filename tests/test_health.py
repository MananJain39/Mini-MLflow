def test_health(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_readiness(api_client):
    resp = api_client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}
