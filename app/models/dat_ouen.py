from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .dat_upload_batch import UploadBatch
    from .mst_user import User


class OuenData(db.Model):
    __tablename__ = 'dat_応援連絡票'

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column('ファイルID', ForeignKey('dat_ファイル.id'), nullable=False)
    from_district: Mapped[str] = mapped_column('送り出し_地区', String(20), nullable=False)
    from_section_code: Mapped[str] = mapped_column('送り出し_課コード', String(20), nullable=False)
    to_district: Mapped[str] = mapped_column('受け入れ_地区', String(20), nullable=False)
    to_section_code: Mapped[str] = mapped_column('受け入れ_課コード', String(20), nullable=False)
    departure_date: Mapped[Optional[date]] = mapped_column('出課日', Date)
    return_date: Mapped[Optional[date]] = mapped_column('帰課日', Date)
    days: Mapped[int] = mapped_column('日数', Integer, nullable=False)
    extended_days: Mapped[int] = mapped_column('延日数', Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column('備考', String(255))
    created_at: Mapped[datetime] = mapped_column(
        '登録日時', DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column('登録者ID', Integer, nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='ouen_records')

    def __repr__(self) -> str:
        return f'<OuenData from={self.from_section_code} to={self.to_section_code}>'
