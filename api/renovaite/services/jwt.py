from datetime import UTC, datetime, timedelta

import jwt

from renovaite.settings.base import get_settings


def create_token_pair(user_id: int) -> dict[str, str]:
    settings = get_settings()
    now = datetime.now(UTC)

    access_payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": now + timedelta(minutes=settings.access_token_lifetime_minutes),
        "iat": now,
    }
    refresh_payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": now + timedelta(days=settings.refresh_token_lifetime_days),
        "iat": now,
    }

    access = jwt.encode(access_payload, settings.secret_key, algorithm="HS256")
    refresh = jwt.encode(refresh_payload, settings.secret_key, algorithm="HS256")

    return {"access": access, "refresh": refresh}


def decode_token(token: str, expected_type: str) -> dict[str, object]:
    settings = get_settings()
    payload: dict[str, object] = jwt.decode(
        token, settings.secret_key, algorithms=["HS256"]
    )
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"expected token type '{expected_type}'")
    return payload
