import os
from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(UTC).isoformat()),
    }


@router.get("/version")
def version() -> dict[str, str]:
    return {
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(UTC).isoformat()),
    }
