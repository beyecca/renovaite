import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from renovaite.models.magic_link import MagicLinkToken
from renovaite.models.user import User
from renovaite.services.email import send_magic_link_email
from renovaite.services.jwt import create_token_pair
from renovaite.settings.base import get_settings

logger = logging.getLogger(__name__)


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
        try:
            token = MagicLinkToken(email=user.email, expires_at=expiry)
            db.add(token)
            db.commit()
            db.refresh(token)
            MagicLinkService._send_email(email=email, token=str(token.token))
        except Exception:
            logger.exception("Failed to send magic link email to %s", email)
            db.rollback()
            # Don't re-raise — response is always 200 to prevent account enumeration.

    @staticmethod
    def verify(token_id: uuid.UUID, db: Session) -> User:
        """
        Validate a magic link token and return the associated user.
        Marks the token as used and soft-deleted on success.
        Raises ValueError on invalid, expired, or already-used tokens.
        """
        token = db.exec(
            select(MagicLinkToken).where(
                MagicLinkToken.token == token_id,
                MagicLinkToken.is_deleted == False,  # noqa: E712
            )
        ).first()

        if token is None:
            raise ValueError("invalid token")

        if token.used_at is not None:
            raise ValueError("token already used")

        if datetime.now(UTC) > token.expires_at.replace(tzinfo=UTC):
            raise ValueError("token expired")

        users = db.exec(select(User).where(User.email == token.email)).all()
        if len(users) != 1:
            raise ValueError("user not found")
        user = users[0]

        token.used_at = datetime.now(UTC)
        token.updated_at = datetime.now(UTC)
        token.is_deleted = True
        db.add(token)
        db.commit()
        db.refresh(token)

        return user

    @staticmethod
    def _send_email(email: str, token: str) -> None:
        send_magic_link_email(email=email, token=token)

    @staticmethod
    def verify_and_issue_tokens(token_id: uuid.UUID, db: Session) -> tuple[str, str]:
        """Verify a magic link token and return (access_token, refresh_token)."""
        user = MagicLinkService.verify(token_id, db)
        pair = create_token_pair(user.id)  # type: ignore[arg-type]
        return pair["access"], pair["refresh"]
