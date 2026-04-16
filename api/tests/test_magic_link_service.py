import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from renovaite.models.magic_link import MagicLinkToken
from renovaite.services.magic_link import MagicLinkService

# ---------------------------------------------------------------------------
# MagicLinkService.request
# ---------------------------------------------------------------------------


def test_request_creates_token_for_known_user(user, db):
    with patch(
        "renovaite.services.magic_link.MagicLinkService._send_email"
    ) as mock_send:
        MagicLinkService.request(email="test@example.com", db=db)

    token = db.exec(
        __import__("sqlmodel")
        .select(MagicLinkToken)
        .where(MagicLinkToken.email == "test@example.com")
    ).first()
    assert token is not None
    mock_send.assert_called_once()


def test_request_does_nothing_silently_for_unknown_email(db):
    with patch(
        "renovaite.services.magic_link.MagicLinkService._send_email"
    ) as mock_send:
        MagicLinkService.request(email="nobody@example.com", db=db)

    token = db.exec(
        __import__("sqlmodel")
        .select(MagicLinkToken)
        .where(MagicLinkToken.email == "nobody@example.com")
    ).first()
    assert token is None
    mock_send.assert_not_called()


def test_request_sends_email_with_token(user, db):
    with patch(
        "renovaite.services.magic_link.MagicLinkService._send_email"
    ) as mock_send:
        MagicLinkService.request(email="test@example.com", db=db)

    call_kwargs = mock_send.call_args
    assert call_kwargs is not None
    assert "test@example.com" in str(call_kwargs)


# ---------------------------------------------------------------------------
# MagicLinkService.verify
# ---------------------------------------------------------------------------


def test_verify_returns_user_for_valid_token(user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    result = MagicLinkService.verify(token.token, db=db)
    assert result.email == user.email


def test_verify_marks_token_as_used(user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    MagicLinkService.verify(token.token, db=db)

    db.refresh(token)
    assert token.used_at is not None


def test_verify_raises_for_expired_token(user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    with pytest.raises(ValueError, match="expired"):
        MagicLinkService.verify(token.token, db=db)


def test_verify_raises_for_used_token(user, db):
    token = MagicLinkToken(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        used_at=datetime.now(UTC),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    with pytest.raises(ValueError, match="used"):
        MagicLinkService.verify(token.token, db=db)


def test_verify_raises_for_invalid_token(db):
    with pytest.raises(ValueError, match="invalid"):
        MagicLinkService.verify(uuid.uuid4(), db=db)
