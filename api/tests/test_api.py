import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_healthz_returns_ok():
    client = Client()
    resp = client.get("/api/healthz")

    assert resp.status_code == 200

    data = json.loads(resp.content)
    assert data["status"] == "ok"
    assert data["service"] == "api"
    assert "git_sha" in data
    assert "build_time" in data
