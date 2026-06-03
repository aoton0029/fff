from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, login_manager

if TYPE_CHECKING:
    from .dat_upload_batch import UploadBatch


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # upload_batches: Mapped[list[UploadBatch]] = relationship(
    #     'UploadBatch',
    #     primaryjoin='User.id == foreign(UploadBatch.created_by)',
    #     viewonly=True,
    # )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
