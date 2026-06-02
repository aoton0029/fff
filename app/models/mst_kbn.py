from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class KbnMaster(db.Model):
    __tablename__ = 'mst_区分'

    kbn_code: Mapped[str] = mapped_column('区分コード', String(20), primary_key=True)
    kbn_name: Mapped[str] = mapped_column('区分名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<KbnMaster {self.kbn_code} {self.kbn_name}>'
