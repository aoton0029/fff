from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .mst_account import AccountMaster
    from .mst_cost_center import CostCenterMaster
    from .mst_district import DistrictMaster
    from .mst_section import SectionMaster


class DepartmentMaster(db.Model):
    __tablename__ = 'mst_変換マスタ'

    department_code: Mapped[str] = mapped_column('行ラベル', String(20), primary_key=True)
    department_name: Mapped[str] = mapped_column('行名', String(100), nullable=False)
    district_code: Mapped[str] = mapped_column('地区コード', String(20), nullable=False)
    section_code: Mapped[str] = mapped_column(
        '課コード', String(20), ForeignKey('mst_課コード.課コード'), nullable=False
    )
    agg_section_code: Mapped[str] = mapped_column(
        '集約課コード', String(20), ForeignKey('mst_課コード.課コード'), nullable=False
    )
    kbn_code: Mapped[str] = mapped_column('区分コード', String(20), nullable=False)
    account_code: Mapped[str] = mapped_column('勘定科目コード', String(20), nullable=False)
    cost_center_code: Mapped[str] = mapped_column('原価センタコード', String(20), nullable=False)

    def __repr__(self) -> str:
        return f'<DepartmentMaster {self.department_code} {self.department_name}>'
