from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class LaborUnitPrice(db.Model):
    __tablename__ = 'dat_労務費単価'

    id: Mapped[int] = mapped_column(primary_key=True)
    year_month: Mapped[str] = mapped_column('年月', String(7), nullable=False, unique=True)
    unit_price: Mapped[float] = mapped_column('単価', Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f'<LaborUnitPrice {self.year_month} {self.unit_price}>'
