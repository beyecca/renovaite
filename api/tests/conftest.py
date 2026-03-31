import os

# Set before any settings are loaded so mail_console=True for all tests
os.environ.setdefault("MAIL_CONSOLE", "true")

import pytest

# Import models so SQLModel metadata is populated before create_all
import renovaite.models  # noqa: F401
from renovaite.db import get_session
from renovaite.main import app
from renovaite.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel
from starlette.testclient import TestClient


@pytest.fixture
def engine():
    # StaticPool shares a single connection so in-memory tables are visible
    # across the test thread and FastAPI's threadpool.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def db(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(db):
    def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    u = User(email="test@example.com")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
