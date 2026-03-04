from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from renovaite.models.magic_link import MagicLinkToken


def send_magic_link_email(email: str, token: str) -> None:
    verify_url = f"{settings.MAGIC_LINK_BASE_URL}/auth/verify?token={token}"
    send_mail(
        subject="Your Renovaite login link",
        message=f"Click the link below to log in. It expires in {settings.MAGIC_LINK_EXPIRY_MINUTES} minutes.\n\n{verify_url}",
        from_email="noreply@renovaite.com",
        recipient_list=[email],
        fail_silently=False,
    )


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
        try:
            token = MagicLinkToken.objects.get(token=token_str)
        except (MagicLinkToken.DoesNotExist, Exception):
            raise ValueError("invalid token") from None

        if token.used_at is not None:
            raise ValueError("token already used")

        if timezone.now() > token.expires_at:
            raise ValueError("token expired")

        token.used_at = timezone.now()
        token.save(update_fields=["used_at"])

        try:
            return User.objects.get(email=token.email)
        except User.DoesNotExist:
            raise ValueError("invalid token") from None
