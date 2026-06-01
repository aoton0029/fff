from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .allocation import AllocationData
    from .labor_transfer import LaborTransferData
    from .ouen import OuenData
    from .salary import SalaryData
    from .user import User


class UploadBatch(db.Model):
    __tablename__ = 'upload_batches'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # salary / allocation / labor_transfer / ouen
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    creator: Mapped[User] = relationship(back_populates='upload_batches')
    salary_records: Mapped[list[SalaryData]] = relationship(back_populates='batch')
    allocation_records: Mapped[list[AllocationData]] = relationship(back_populates='batch')
    labor_transfer_records: Mapped[list[LaborTransferData]] = relationship(back_populates='batch')
    ouen_records: Mapped[list[OuenData]] = relationship(back_populates='batch')

    def __repr__(self) -> str:
        return f'<UploadBatch {self.file_name} ({self.file_type})>'
