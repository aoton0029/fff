from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Generic, TypeVar

import pandas as pd
from flask_login import UserMixin
from werkzeug.security import check_password_hash

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _nullable_str(val: object) -> str | None:
    """Return None for NULL/NaN, otherwise str(val)."""
    return None if pd.isna(val) else str(val)


def _nullable_int(val: object) -> int | None:
    """Return None for NULL/NaN, otherwise int(val)."""
    return None if pd.isna(val) else int(val)  # type: ignore[arg-type]


def _nullable_dt(val: object) -> datetime | None:
    """Return None for NULL/NaN/NaT, otherwise a pandas Timestamp.

    Handles SQLite (stores datetimes as text), MSSQL (native datetime),
    and already-parsed pandas Timestamp / Python datetime objects.
    """
    if pd.isna(val):
        return None
    ts = pd.to_datetime(val)
    return None if pd.isna(ts) else ts  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Domain records
# ---------------------------------------------------------------------------

@dataclass
class FileRecord:
    """Lightweight representation of an *uploaded_files* row.

    Replaces the :class:`~app.models.file.UploadedFile` ORM object in the
    service / template layer.  Compatible with Jinja2 attribute access and
    all existing templates (``file.id``, ``file.original_filename``, etc.).
    """

    id: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    status: str
    mime_type: str | None = None
    row_count: int | None = None
    sheet_names: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    @classmethod
    def from_row(cls, row: pd.Series) -> FileRecord:
        """Construct a :class:`FileRecord` from a pandas Series (one DB row)."""
        return cls(
            id=int(row["id"]),
            original_filename=str(row["original_filename"]),
            stored_filename=str(row["stored_filename"]),
            file_path=str(row["file_path"]),
            file_size=int(row["file_size"]),
            status=str(row["status"]),
            mime_type=_nullable_str(row["mime_type"]),
            row_count=_nullable_int(row["row_count"]),
            sheet_names=_nullable_str(row["sheet_names"]),
            error_message=_nullable_str(row["error_message"]),
            created_at=_nullable_dt(row["created_at"]),
            updated_at=_nullable_dt(row["updated_at"]),
            created_by=_nullable_str(row["created_by"]),
            updated_by=_nullable_str(row["updated_by"]),
        )


@dataclass
class UserRecord(UserMixin):
    """Lightweight representation of a *users* row.

    Implements the :class:`~flask_login.UserMixin` interface so it can be
    passed directly to :func:`~flask_login.login_user` and stored in the
    Flask-Login session without depending on the ORM :class:`~app.models.user.User`.
    """

    id: int
    username: str
    password_hash: str
    role: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    # Flask-Login requires get_id() to return a string.
    def get_id(self) -> str:
        return str(self.id)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def from_row(cls, row: pd.Series) -> UserRecord:
        """Construct a :class:`UserRecord` from a pandas Series (one DB row)."""
        return cls(
            id=int(row["id"]),
            username=str(row["username"]),
            password_hash=str(row["password_hash"]),
            role=str(row["role"]),
            created_at=_nullable_dt(row["created_at"]),
            updated_at=_nullable_dt(row["updated_at"]),
            created_by=_nullable_str(row["created_by"]),
            updated_by=_nullable_str(row["updated_by"]),
        )


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

@dataclass
class SimplePagination(Generic[T]):
    """Drop-in replacement for Flask-SQLAlchemy's ``Pagination`` object.

    The API and view layer already destructures ``pagination.page``,
    ``pagination.total``, and ``pagination.items``, so this dataclass is
    fully compatible without template changes.
    """

    items: list[T]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        return ceil(self.total / self.per_page) if self.per_page else 0

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages
