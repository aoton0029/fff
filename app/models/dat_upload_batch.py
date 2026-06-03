from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .dat_allocation import AllocationData
    from .dat_labor_transfer import LaborTransferData
    from .dat_ouen import OuenData
    from .dat_salary import SalaryData
    from .mst_filetype import FileTypeMaster
    from .mst_user import User


class UploadBatch(db.Model):
    __tablename__ = 'dat_ファイル'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), ForeignKey('mst_ファイルタイプ.ファイルタイプコード'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    salary_records: Mapped[list[SalaryData]] = relationship(back_populates='batch')
    allocation_records: Mapped[list[AllocationData]] = relationship(back_populates='batch')
    labor_transfer_records: Mapped[list[LaborTransferData]] = relationship(back_populates='batch')
    ouen_records: Mapped[list[OuenData]] = relationship(back_populates='batch')

    creator: Mapped[User] = relationship(
        'User', foreign_keys=[created_by], viewonly=True
    )
    file_type_master: Mapped[FileTypeMaster] = relationship(
        'FileTypeMaster', foreign_keys=[file_type], viewonly=True
    )

    def __repr__(self) -> str:
        return f'<UploadBatch {self.file_name} ({self.file_type})>'
