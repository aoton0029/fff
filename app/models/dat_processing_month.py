from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .mst_user import User


class ProcessingMonth(db.Model):
    """月次処理の処理年月を保持するシングルレコードテーブル。"""
    __tablename__ = 'dat_月次処理年月'

    id: Mapped[int] = mapped_column(primary_key=True)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by: Mapped[int] = mapped_column(Integer, nullable=False)


    def __repr__(self) -> str:
        return f'<ProcessingMonth {self.year_month}>'
