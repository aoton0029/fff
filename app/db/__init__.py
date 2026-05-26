from .manager import DbManager
from .records import FileRecord, SimplePagination, UserRecord
from ..extensions import db

# Application-scoped singleton.
# Flask-SQLAlchemy's `db` manages the connection pool and request-scoped
# sessions, so a single DbManager instance is safe to share across threads.
db_manager = DbManager(db)

__all__ = [
    "DbManager",
    "db_manager",
    "FileRecord",
    "UserRecord",
    "SimplePagination",
]
