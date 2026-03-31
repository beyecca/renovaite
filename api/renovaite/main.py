from fastapi import FastAPI

from renovaite.api.auth import router as auth_router
from renovaite.api.health import router as health_router

app = FastAPI(title="Renovaite API", version="0.1.0")

app.include_router(auth_router, prefix="/api")
app.include_router(health_router, prefix="/api")
