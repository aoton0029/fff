from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .upload_batch import UploadBatch
    from .user import User


class LaborTransferData(db.Model):
    __tablename__ = 'dat_労務費振替依頼書'

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey('dat_ファイル.id'), nullable=False)
    account_code: Mapped[str] = mapped_column('勘定科目コード', String(30), nullable=False)
    cost_center: Mapped[Optional[str]] = mapped_column('原価センタ', String(30))
    burden_section: Mapped[Optional[str]] = mapped_column('負担課', String(30))
    charge_section: Mapped[str] = mapped_column('担当課', String(30), nullable=False)
    construction_name: Mapped[Optional[str]] = mapped_column('工事名', String(200))
    work_hours: Mapped[float] = mapped_column('作業時間', Float, nullable=False)
    wbs: Mapped[Optional[str]] = mapped_column('WBS', String(100))
    asset_number: Mapped[Optional[str]] = mapped_column('資産集約番号', String(50))
    order_number: Mapped[Optional[str]] = mapped_column('指図', String(50))
    note: Mapped[Optional[str]] = mapped_column('備考', String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='labor_transfer_records')
    creator: Mapped[User] = relationship(foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f'<LaborTransferData account={self.account_code} charge={self.charge_section}>'
