import uuid
from datetime import UTC, datetime, timedelta

from renovaite.models.magic_link import MagicLinkToken

# ---------------------------------------------------------------------------
# POST /api/auth/magic-link
# ---------------------------------------------------------------------------


def test_request_magic_link_known_email(client, user):
    resp = client.post(
        "/api/auth/magic-link",
        json={"email": "test@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


def test_request_magic_link_unknown_email(client):
    resp = client.post(
        "/api/auth/magic-link",
        json={"email": "nobody@example.com"},
    )
    # Same response as known email — no account enumeration
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


def test_request_magic_link_invalid_email(client):
    resp = client.post(
        "/api/auth/magic-link",
        json={"email": "not-an-email"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/auth/magic-link/verify
# ---------------------------------------------------------------------------


def _post_verify(client, token):
    return client.post(
        "/api/auth/magic-link/verify",
        json={"token": str(token)},
    )


def test_verify_valid_token(client, user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    resp = _post_verify(client, token.token)
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data
    assert "refresh" in data


def test_verify_expired_token(client, user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    resp = _post_verify(client, token.token)
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == "UNAUTHORIZED"


def test_verify_used_token(client, user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        used_at=datetime.now(UTC),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    resp = _post_verify(client, token.token)
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == "UNAUTHORIZED"


def test_verify_invalid_token(client):
    resp = _post_verify(client, uuid.uuid4())
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == "UNAUTHORIZED"


# ---------------------------------------------------------------------------
# POST /api/auth/token/refresh
# ---------------------------------------------------------------------------


def test_refresh_token_success(client, user):
    from renovaite.services.jwt import create_token_pair

    pair = create_token_pair(user.id)

    resp = client.post(
        "/api/auth/token/refresh",
        json={"refresh": pair["refresh"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data


def test_refresh_token_invalid(client):
    resp = client.post(
        "/api/auth/token/refresh",
        json={"refresh": "not-a-valid-token"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

REG_KEY = "test-reg-key"


def test_register_success(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com"},
        headers={"X-Registration-Key": REG_KEY},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(client, user):
    resp = client.post(
        "/api/auth/register",
        json={"email": user.email},
        headers={"X-Registration-Key": REG_KEY},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "CONFLICT"


def test_register_missing_key(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "someone@example.com"},
    )
    assert resp.status_code == 403


def test_register_wrong_key(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "someone@example.com"},
        headers={"X-Registration-Key": "wrong-key"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "FORBIDDEN"


def test_register_disabled(client):
    from renovaite.main import app
    from renovaite.settings.base import Settings, get_settings

    def disabled_settings():
        return Settings(registration_secret_key=None)

    app.dependency_overrides[get_settings] = disabled_settings
    try:
        resp = client.post(
            "/api/auth/register",
            json={"email": "someone@example.com"},
            headers={"X-Registration-Key": REG_KEY},
        )
        assert resp.status_code == 503
        assert resp.json()["detail"]["code"] == "REGISTRATION_DISABLED"
    finally:
        del app.dependency_overrides[get_settings]


def test_register_invalid_email(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "not-an-email"},
        headers={"X-Registration-Key": REG_KEY},
    )
    assert resp.status_code == 422
