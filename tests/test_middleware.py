def test_request_id_middleware(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert "X-Process-Time" in resp.headers
