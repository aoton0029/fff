from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .upload_batch import UploadBatch
    from .user import User


class AllocationData(db.Model):
    __tablename__ = 'dat_工程配賦'

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey('dat_ファイル.id'), nullable=False)
    division_code: Mapped[str] = mapped_column('事業部', String(20), nullable=False)
    district_code: Mapped[str] = mapped_column('地区', String(20), nullable=False)
    section_code: Mapped[str] = mapped_column('課コード', String(20), nullable=False)
    cost_category: Mapped[str] = mapped_column('原価区分', String(20), nullable=False)
    process_code: Mapped[str] = mapped_column('工程', String(20), nullable=False)
    days: Mapped[float] = mapped_column('日数', Float, nullable=False)
    process_name: Mapped[Optional[str]] = mapped_column('工程名', String(100))
    formation: Mapped[float] = mapped_column('編成', Float, nullable=False)
    fixed_count: Mapped[float] = mapped_column('固定', Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='allocation_records')
    creator: Mapped[User] = relationship(foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f'<AllocationData district={self.district_code} section={self.section_code} process={self.process_code}>'
