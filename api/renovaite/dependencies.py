import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from renovaite.db import get_session
from renovaite.models.user import User
from renovaite.services.jwt import decode_token

_security = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    db: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "Authentication required.", "code": "UNAUTHORIZED"},
        )
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or expired token.", "code": "UNAUTHORIZED"},
        ) from exc

    user_id = int(str(payload["sub"]))
    user = db.exec(
        select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
    ).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or expired token.", "code": "UNAUTHORIZED"},
        )
    return user
