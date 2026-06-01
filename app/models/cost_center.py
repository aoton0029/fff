from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class CostCenterMaster(db.Model):
    __tablename__ = 'cost_center_master'

    cost_center_code: Mapped[str] = mapped_column('原価センタコード', String(20), primary_key=True)
    cost_center_name: Mapped[str] = mapped_column('原価センタ名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<CostCenterMaster {self.cost_center_code} {self.cost_center_name}>'
