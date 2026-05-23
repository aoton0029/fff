from ..models.user import User
from ..extensions import db


def authenticate_user(username: str, password: str) -> User | None:
    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar_one_or_none()
    if user is None or not user.check_password(password):
        return None
    return user
