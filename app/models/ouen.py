from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .upload_batch import UploadBatch
    from .user import User


class OuenData(db.Model):
    __tablename__ = 'dat_応援連絡票'

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey('dat_ファイル.id'), nullable=False)
    from_district: Mapped[str] = mapped_column(String(20), nullable=False)
    from_section_code: Mapped[str] = mapped_column(String(20), nullable=False)
    to_district: Mapped[str] = mapped_column(String(20), nullable=False)
    to_section_code: Mapped[str] = mapped_column(String(20), nullable=False)
    departure_date: Mapped[Optional[date]] = mapped_column(Date)
    return_date: Mapped[Optional[date]] = mapped_column(Date)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    extended_days: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='ouen_records')
    creator: Mapped[User] = relationship(foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f'<OuenData from={self.from_section_code} to={self.to_section_code}>'
