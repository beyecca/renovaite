import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="unusedpassword",
    )


# ---------------------------------------------------------------------------
# MagicLinkService.request
# ---------------------------------------------------------------------------


def test_request_creates_token_for_known_user(user):
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    with patch("renovaite.services.magic_link.send_magic_link_email") as mock_send:
        MagicLinkService.request(email="test@example.com")

    assert MagicLinkToken.objects.filter(email="test@example.com").exists()
    mock_send.assert_called_once()


def test_request_does_nothing_silently_for_unknown_email():
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    with patch("renovaite.services.magic_link.send_magic_link_email") as mock_send:
        MagicLinkService.request(email="nobody@example.com")

    assert not MagicLinkToken.objects.filter(email="nobody@example.com").exists()
    mock_send.assert_not_called()


def test_request_sends_email_with_token(user):
    from renovaite.services.magic_link import MagicLinkService

    with patch("renovaite.services.magic_link.send_magic_link_email") as mock_send:
        MagicLinkService.request(email="test@example.com")

    call_kwargs = mock_send.call_args
    assert call_kwargs is not None
    # email and token are passed
    assert "test@example.com" in str(call_kwargs)


# ---------------------------------------------------------------------------
# MagicLinkService.verify
# ---------------------------------------------------------------------------


def test_verify_returns_user_for_valid_token(user):
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() + timezone.timedelta(minutes=15),
    )

    result = MagicLinkService.verify(str(token.token))
    assert result == user


def test_verify_marks_token_as_used(user):
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() + timezone.timedelta(minutes=15),
    )

    MagicLinkService.verify(str(token.token))

    token.refresh_from_db()
    assert token.used_at is not None


def test_verify_raises_for_expired_token(user):
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    with pytest.raises(ValueError, match="expired"):
        MagicLinkService.verify(str(token.token))


def test_verify_raises_for_used_token(user):
    from renovaite.models.magic_link import MagicLinkToken
    from renovaite.services.magic_link import MagicLinkService

    token = MagicLinkToken.objects.create(
        email=user.email,
        token=uuid.uuid4(),
        expires_at=timezone.now() + timezone.timedelta(minutes=15),
        used_at=timezone.now(),
    )

    with pytest.raises(ValueError, match="used"):
        MagicLinkService.verify(str(token.token))


def test_verify_raises_for_invalid_token():
    from renovaite.services.magic_link import MagicLinkService

    with pytest.raises(ValueError, match="invalid"):
        MagicLinkService.verify(str(uuid.uuid4()))
