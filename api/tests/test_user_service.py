import pytest
from renovaite.models.user import User
from renovaite.services.user import UserService
from sqlmodel import Session


def test_create_returns_new_user(db: Session) -> None:
    user = UserService.create(email="new@example.com", db=db)
    assert isinstance(user, User)
    assert user.email == "new@example.com"
    assert user.id is not None


def test_create_raises_for_duplicate_email(db: Session) -> None:
    UserService.create(email="dup@example.com", db=db)
    with pytest.raises(ValueError, match="email already registered"):
        UserService.create(email="dup@example.com", db=db)


def test_create_sets_is_active_true_by_default(db: Session) -> None:
    user = UserService.create(email="active@example.com", db=db)
    assert user.is_active is True


def test_create_sets_is_deleted_false_by_default(db: Session) -> None:
    user = UserService.create(email="notdeleted@example.com", db=db)
    assert user.is_deleted is False
