from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from renovaite.settings.base import get_settings

_engine = None


def get_engine() -> object:
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(settings.database_url, connect_args=connect_args)
    return _engine


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:  # type: ignore[arg-type]
        yield session
