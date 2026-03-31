import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class MagicLinkToken(SQLModel, table=True):
    __tablename__ = "magic_link_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True)
    token: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    used_at: datetime | None = Field(default=None, nullable=True)
    is_deleted: bool = Field(default=False)

    # TODO: add a management command or periodic task to hard-purge tokens where
    # expires_at < now() - timedelta(days=7) to prevent unbounded table growth.

    def __repr__(self) -> str:
        return f"MagicLinkToken({self.email})"
