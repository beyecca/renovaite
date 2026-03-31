from pydantic import BaseModel, EmailStr


class MagicLinkRequestIn(BaseModel):
    email: EmailStr


class MagicLinkRequestOut(BaseModel):
    message: str


class TokenPairOut(BaseModel):
    access: str
    refresh: str


class RefreshTokenIn(BaseModel):
    refresh: str


class ErrorOut(BaseModel):
    error: str
    code: str
