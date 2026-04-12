from sqlmodel import Session, select

from renovaite.models.user import User


class UserService:
    @staticmethod
    def create(email: str, db: Session) -> User:
        existing = db.exec(select(User).where(User.email == email)).first()
        if existing is not None:
            raise ValueError("email already registered")
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
