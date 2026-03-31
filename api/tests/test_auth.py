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
# GET /api/auth/magic-link/verify
# ---------------------------------------------------------------------------


def test_verify_valid_token(client, user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    resp = client.get(f"/api/auth/magic-link/verify?token={token.token}")
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

    resp = client.get(f"/api/auth/magic-link/verify?token={token.token}")
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

    resp = client.get(f"/api/auth/magic-link/verify?token={token.token}")
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == "UNAUTHORIZED"


def test_verify_invalid_token(client):
    resp = client.get(f"/api/auth/magic-link/verify?token={uuid.uuid4()}")
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
