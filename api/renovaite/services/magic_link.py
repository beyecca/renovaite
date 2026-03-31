import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from renovaite.models.magic_link import MagicLinkToken
from renovaite.models.user import User
from renovaite.services.email import send_magic_link_email
from renovaite.settings.base import get_settings


class MagicLinkService:
    @staticmethod
    def request(email: str, db: Session) -> None:
        """
        Create a magic link token and send an email.
        If the email is not registered, do nothing silently (no account enumeration).
        """
        user = db.exec(select(User).where(User.email == email)).first()
        if user is None:
            return

        settings = get_settings()
        expiry = datetime.now(UTC) + timedelta(
            minutes=settings.magic_link_expiry_minutes
        )
        token = MagicLinkToken(email=user.email, expires_at=expiry)
        db.add(token)
        db.commit()
        db.refresh(token)

        send_magic_link_email(email=email, token=str(token.token))

    @staticmethod
    def verify(token_str: str, db: Session) -> User:
        """
        Validate a magic link token and return the associated user.
        Marks the token as used on success.
        Raises ValueError on invalid, expired, or already-used tokens.
        """
        try:
            token_uuid = uuid.UUID(token_str)
        except (ValueError, AttributeError):
            raise ValueError("invalid token") from None

        token = db.exec(
            select(MagicLinkToken).where(MagicLinkToken.token == token_uuid)
        ).first()

        if token is None:
            raise ValueError("invalid token")

        if token.used_at is not None:
            raise ValueError("token already used")

        if datetime.now(UTC) > token.expires_at.replace(tzinfo=UTC):
            raise ValueError("token expired")

        token.used_at = datetime.now(UTC)
        db.add(token)
        db.commit()
        db.refresh(token)

        user = db.exec(select(User).where(User.email == token.email)).first()
        if user is None:
            raise ValueError("invalid token")

        return user
