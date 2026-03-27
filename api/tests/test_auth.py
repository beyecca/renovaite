import json
import uuid

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="unusedpassword",
    )


# ---------------------------------------------------------------------------
# POST /api/auth/magic-link
# ---------------------------------------------------------------------------


def test_request_magic_link_known_email(client, user):
    resp = client.post(
        "/api/auth/magic-link",
        data=json.dumps({"email": "test@example.com"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert "message" in data


def test_request_magic_link_unknown_email(client):
    resp = client.post(
        "/api/auth/magic-link",
        data=json.dumps({"email": "nobody@example.com"}),
        content_type="application/json",
    )
    # Same response as known email — no account enumeration
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert "message" in data


def test_request_magic_link_invalid_email(client):
    resp = client.post(
        "/api/auth/magic-link",
        data=json.dumps({"email": "not-an-email"}),
        content_type="application/json",
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/auth/magic-link/verify
# ---------------------------------------------------------------------------


def _post_verify(client, token):
    return client.post(
        "/api/auth/magic-link/verify",
        data=json.dumps({"token": str(token)}),
        content_type="application/json",
    )


def test_verify_valid_token(client, user):
    from renovaite.models.magic_link import MagicLinkToken

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() + timezone.timedelta(minutes=15),
    )

    resp = _post_verify(client, token.token)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert "access" in data
    assert "refresh" in data


def test_verify_expired_token(client, user):
    from renovaite.models.magic_link import MagicLinkToken

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    resp = _post_verify(client, token.token)
    assert resp.status_code == 401
    data = json.loads(resp.content)
    assert data["code"] == "UNAUTHORIZED"


def test_verify_used_token(client, user):
    from renovaite.models.magic_link import MagicLinkToken

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() + timezone.timedelta(minutes=15),
        used_at=timezone.now(),
    )

    resp = _post_verify(client, token.token)
    assert resp.status_code == 401
    data = json.loads(resp.content)
    assert data["code"] == "UNAUTHORIZED"


def test_verify_invalid_token(client):
    resp = _post_verify(client, uuid.uuid4())
    assert resp.status_code == 401
    data = json.loads(resp.content)
    assert data["code"] == "UNAUTHORIZED"


# ---------------------------------------------------------------------------
# POST /api/auth/token/refresh
# ---------------------------------------------------------------------------


def test_refresh_token_success(client, user):
    from ninja_jwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)

    resp = client.post(
        "/api/auth/token/refresh",
        data=json.dumps({"refresh": str(refresh)}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert "access" in data


def test_refresh_token_invalid(client):
    resp = client.post(
        "/api/auth/token/refresh",
        data=json.dumps({"refresh": "not-a-valid-token"}),
        content_type="application/json",
    )
    assert resp.status_code == 401
