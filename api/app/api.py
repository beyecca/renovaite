from ninja import NinjaAPI
import os
from datetime import datetime, timezone

api = NinjaAPI(title="RenoBrain API")


@api.get("/healthz")
def healthz(request):
    return {"status": "ok"}

@api.get("/version")
def version(request):
    return {
        "service": "api",
        "git_sha": os.getenv("GIT_SHA", "dev"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(timezone.utc).isoformat()),
    }