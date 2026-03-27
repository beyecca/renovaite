from uuid import UUID

from ninja import Schema
from pydantic import EmailStr


class MagicLinkRequestIn(Schema):
    email: EmailStr


class MagicLinkRequestOut(Schema):
    message: str


class TokenPairOut(Schema):
    access: str
    refresh: str


class ErrorOut(Schema):
    error: str
    code: str


class MagicLinkVerifyIn(Schema):
    token: UUID
