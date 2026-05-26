<<<<<<< HEAD
# Deprecated: use app.auth.service
from ..auth.service import authenticate_user  # noqa: F401

__all__ = ["authenticate_user"]
=======
from ..db import db_manager
from ..db.records import UserRecord


def authenticate_user(username: str, password: str) -> UserRecord | None:
    df = db_manager.fetch(
        "SELECT * FROM users WHERE username = :username",
        {"username": username},
    )
    if df.empty:
        return None
    user = UserRecord.from_row(df.iloc[0])
    if not user.check_password(password):
        return None
    return user
>>>>>>> 4338afad389814a878391d7019d553facd2a4f71
