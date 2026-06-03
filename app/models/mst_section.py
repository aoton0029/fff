from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .mst_cost_center import CostCenterMaster
    from .mst_district import DistrictMaster


class SectionMaster(db.Model):
    __tablename__ = 'mst_課コード'

    section_code: Mapped[str] = mapped_column('課コード', String(20), primary_key=True)
    section_name: Mapped[str] = mapped_column('課名', String(100), nullable=False)
    district_code: Mapped[str] = mapped_column('地区コード', String(20), ForeignKey('mst_地区.地区コード'), nullable=False)
    cost_center_code: Mapped[str] = mapped_column('原価センタコード', String(20), ForeignKey('mst_原価センタ.原価センタコード'), nullable=False)

    district: Mapped[DistrictMaster] = relationship(
        'DistrictMaster',
        foreign_keys=[district_code],
        viewonly=True,
    )
    cost_center: Mapped[CostCenterMaster] = relationship(
        'CostCenterMaster',
        foreign_keys=[cost_center_code],
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f'<SectionMaster {self.section_code} {self.section_name}>'
