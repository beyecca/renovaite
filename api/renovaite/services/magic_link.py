import logging
from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from ninja_jwt.tokens import RefreshToken

from renovaite.models.magic_link import MagicLinkToken

logger = logging.getLogger(__name__)

# TODO: move send_magic_link_email to MagicLinkService._send_email to make it
# private to the service interface, consistent with the services pattern.


class MagicLinkService:
    @staticmethod
    def request(email: str) -> None:
        """
        Create a magic link token and send an email.
        If the email is not registered, do nothing silently (no account enumeration).
        """
        user = User.objects.filter(email=email).first()
        if user is None:
            return

        expiry = timezone.now() + timedelta(minutes=settings.MAGIC_LINK_EXPIRY_MINUTES)
        try:
            with transaction.atomic():
                token = MagicLinkToken.objects.create(
                    email=user.email, expires_at=expiry
                )
                send_magic_link_email(email=email, token=str(token.token))
        except Exception:
            logger.exception("Failed to send magic link email to %s", email)
            # Don't re-raise — response is always 200 to prevent account enumeration.

    @staticmethod
    def verify(token_id: UUID) -> User:
        """
        Validate a magic link token and return the associated user.
        Marks the token as used on success.
        Raises ValueError on invalid, expired, or already-used tokens.
        """
        with transaction.atomic():
            try:
                token = MagicLinkToken.objects.select_for_update().get(
                    token=token_id, is_deleted=False
                )
            except MagicLinkToken.DoesNotExist:
                raise ValueError("invalid token") from None

            if token.used_at is not None:
                raise ValueError("token already used")
            if timezone.now() > token.expires_at:
                raise ValueError("token expired")

            try:
                user = User.objects.get(email=token.email)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                raise ValueError("user not found") from None

            token.used_at = timezone.now()
            token.is_deleted = True
            token.save(update_fields=["used_at", "is_deleted", "updated_at"])

        return user

    @staticmethod
    def verify_and_issue_tokens(token_id: UUID) -> tuple[str, str]:
        """Verify a magic link token and return (access_token, refresh_token)."""
        user = MagicLinkService.verify(token_id)
        refresh: RefreshToken = RefreshToken.for_user(user)  # type: ignore[assignment]
        return str(refresh.access_token), str(refresh)


def send_magic_link_email(email: str, token: str) -> None:
    verify_url = f"{settings.MAGIC_LINK_BASE_URL}/auth/verify?token={token}"
    send_mail(
        subject="Your Renovaite login link",
        message=f"Click the link below to log in. It expires in {settings.MAGIC_LINK_EXPIRY_MINUTES} minutes.\n\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
