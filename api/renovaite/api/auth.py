import jwt
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from renovaite.db import get_session
from renovaite.models.user import User
from renovaite.schemas.auth import (
    ErrorOut,
    MagicLinkRequestIn,
    MagicLinkRequestOut,
    MagicLinkVerifyIn,
    RefreshTokenIn,
    TokenPairOut,
)
from renovaite.services.jwt import create_token_pair, decode_token
from renovaite.services.magic_link import MagicLinkService

router = APIRouter(prefix="/auth", tags=["auth"])


# TODO(pre-launch): add per-IP rate limiting (e.g. slowapi 5/min) to prevent
# email spam abuse. This endpoint is fully public and unbounded.
@router.post("/magic-link", response_model=MagicLinkRequestOut)
def request_magic_link(
    payload: MagicLinkRequestIn,
    db: Session = Depends(get_session),
) -> MagicLinkRequestOut:
    MagicLinkService.request(email=str(payload.email), db=db)
    return MagicLinkRequestOut(
        message="If that email is registered, you'll receive a login link shortly."
    )


@router.post("/magic-link/verify")
def verify_magic_link(
    payload: MagicLinkVerifyIn,
    db: Session = Depends(get_session),
) -> JSONResponse:
    try:
        access, refresh = MagicLinkService.verify_and_issue_tokens(payload.token, db=db)
    except ValueError:
        return JSONResponse(
            status_code=401,
            content=ErrorOut(
                error="Invalid or expired token.", code="UNAUTHORIZED"
            ).model_dump(),
        )

    return JSONResponse(
        status_code=200,
        content=TokenPairOut(access=access, refresh=refresh).model_dump(),
    )


@router.post("/token/refresh")
def refresh_token(
    payload: RefreshTokenIn,
    db: Session = Depends(get_session),
) -> JSONResponse:
    try:
        data = decode_token(payload.refresh, expected_type="refresh")
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content=ErrorOut(
                error="Invalid or expired token.", code="UNAUTHORIZED"
            ).model_dump(),
        )

    user_id = int(str(data["sub"]))
    user = db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        return JSONResponse(
            status_code=401,
            content=ErrorOut(
                error="Invalid or expired token.", code="UNAUTHORIZED"
            ).model_dump(),
        )

    pair = create_token_pair(user_id)
    return JSONResponse(status_code=200, content={"access": pair["access"]})
