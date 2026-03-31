def test_healthz_returns_ok(client):
    resp = client.get("/api/healthz")

    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "api"
    assert "git_sha" in data
    assert "build_time" in data
