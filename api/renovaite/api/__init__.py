import os
from datetime import UTC, datetime

from django.http import HttpRequest
from ninja import NinjaAPI, Router
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings
from ninja_jwt.tokens import RefreshToken

from renovaite.schemas.auth import (
    ErrorOut,
    MagicLinkRequestIn,
    MagicLinkRequestOut,
    MagicLinkVerifyIn,
    TokenPairOut,
)
from renovaite.services.magic_link import MagicLinkService

api = NinjaAPI(title="Renovaite API", version="0.1.0", auth=JWTAuth())
_schema = SchemaControl(api_settings)
auth_router = Router(tags=["auth"])


# TODO(pre-launch): add per-IP rate limiting (e.g. django-ratelimit 5/min) to prevent
# email spam abuse. This endpoint is fully public and unbounded.
@auth_router.post(
    "/magic-link",
    response=MagicLinkRequestOut,
    auth=None,
    url_name="magic_link_request",
)
def request_magic_link(
    request: HttpRequest, payload: MagicLinkRequestIn
) -> MagicLinkRequestOut:
    MagicLinkService.request(email=payload.email)
    return MagicLinkRequestOut(
        message="If that email is registered, you'll receive a login link shortly."
    )


@auth_router.post(
    "/magic-link/verify",
    response={200: TokenPairOut, 401: ErrorOut},
    auth=None,
    url_name="magic_link_verify",
)
def verify_magic_link(
    request: HttpRequest, payload: MagicLinkVerifyIn
) -> tuple[int, TokenPairOut | ErrorOut]:
    try:
        user = MagicLinkService.verify(payload.token)
    except ValueError:
        return 401, ErrorOut(error="Invalid or expired token.", code="UNAUTHORIZED")

    refresh: RefreshToken = RefreshToken.for_user(user)  # type: ignore[assignment]
    return 200, TokenPairOut(access=str(refresh.access_token), refresh=str(refresh))


@auth_router.post(
    "/token/refresh",
    response=_schema.obtain_pair_refresh_schema.get_response_schema(),
    auth=None,
    url_name="token_refresh",
)
def refresh_token(
    request: HttpRequest,
    refresh_token: _schema.obtain_pair_refresh_schema,  # type: ignore[name-defined]
) -> object:
    return refresh_token.to_response_schema()


api.add_router("/auth", auth_router)


@api.get("/healthz", auth=None)
def healthz(request: HttpRequest) -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(UTC).isoformat()),
    }


@api.get("/version", auth=None)
def version(request: HttpRequest) -> dict[str, str]:
    return {
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(UTC).isoformat()),
    }
