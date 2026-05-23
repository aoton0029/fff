from sqlalchemy import select
from .extensions import db
from .models.user import User


def seed_db() -> None:
    """Insert initial records if they do not already exist."""
    _seed_users()


def _seed_users() -> None:
    initial_users = [
        {"username": "admin", "password": "admin", "role": "admin"},
    ]
    for data in initial_users:
        exists = db.session.scalar(select(User).filter_by(username=data["username"]))
        if exists is None:
            user = User(username=data["username"], role=data["role"])
            user.set_password(data["password"])
            db.session.add(user)
    db.session.commit()
