from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from renovaite.models.magic_link import MagicLinkToken


class MagicLinkService:
    @staticmethod
    def request(email: str) -> None:
        """
        Create a magic link token and send an email.
        If the email is not registered, do nothing silently (no account enumeration).
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        expiry = timezone.now() + timedelta(minutes=settings.MAGIC_LINK_EXPIRY_MINUTES)
        token = MagicLinkToken.objects.create(email=user.email, expires_at=expiry)
        send_magic_link_email(email=email, token=str(token.token))

    @staticmethod
    def verify(token_str: str) -> User:
        """
        Validate a magic link token and return the associated user.
        Marks the token as used on success.
        Raises ValueError on invalid, expired, or already-used tokens.
        """
        with transaction.atomic():
            try:
                token = MagicLinkToken.objects.select_for_update().get(token=token_str)
            except MagicLinkToken.DoesNotExist:
                raise ValueError("invalid token") from None

            if token.used_at is not None:
                raise ValueError("token already used")
            if timezone.now() > token.expires_at:
                raise ValueError("token expired")

            token.used_at = timezone.now()
            token.is_deleted = True
            token.save(update_fields=["used_at", "is_deleted", "updated_at"])

        return User.objects.get(email=token.email)


def send_magic_link_email(email: str, token: str) -> None:
    verify_url = f"{settings.MAGIC_LINK_BASE_URL}/auth/verify?token={token}"
    send_mail(
        subject="Your Renovaite login link",
        message=f"Click the link below to log in. It expires in {settings.MAGIC_LINK_EXPIRY_MINUTES} minutes.\n\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
