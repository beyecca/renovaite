import os
from datetime import UTC, datetime

from django.http import HttpRequest
from ninja import NinjaAPI

api = NinjaAPI(title="RenoBrain API")


@api.get("/healthz")
def healthz(request: HttpRequest) -> dict[str, str]:
    return {"status": "ok"}


@api.get("/version")
def version(request: HttpRequest) -> dict[str, str]:
    return {
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(UTC).isoformat()),
    }
