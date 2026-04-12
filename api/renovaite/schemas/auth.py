import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class MagicLinkRequestIn(BaseModel):
    email: EmailStr


class MagicLinkRequestOut(BaseModel):
    message: str


class MagicLinkVerifyIn(BaseModel):
    token: uuid.UUID


class TokenPairOut(BaseModel):
    access: str
    refresh: str


class RefreshTokenIn(BaseModel):
    refresh: str


class ErrorOut(BaseModel):
    error: str
    code: str


class RegisterIn(BaseModel):
    email: EmailStr


class RegisterOut(BaseModel):
    id: int
    email: str
    created_at: datetime
