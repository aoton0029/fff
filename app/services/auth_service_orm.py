"""ORM-based authentication service.

Comparison pattern against auth_service.py (db / raw-SQL pattern).

db パターン          → db_manager.fetch(sql) → pd.DataFrame → UserRecord (dataclass)
ORM パターン (here)  → db.session.execute(select(User)) → User (ORM model)
"""

from sqlalchemy import select

from ..extensions import db
from ..models import User


def authenticate_user(username: str, password: str) -> User | None:
    """Return the matching ``User`` ORM instance, or ``None`` on failure.

    db パターンとの対比
    -------------------
    db  : db_manager.fetch("SELECT * FROM users WHERE username = :u", ...)
          → pd.DataFrame → UserRecord.from_row(df.iloc[0])
    ORM : db.session.execute(select(User).where(...)).scalar_one_or_none()
    """
    user: User | None = db.session.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    if user is None or not user.check_password(password):
        return None
    return user
