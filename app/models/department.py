from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .account import AccountMaster
    from .cost_center import CostCenterMaster
    from .district import DistrictMaster
    from .section import SectionMaster


class DepartmentMaster(db.Model):
    __tablename__ = 'department_master'

    department_code: Mapped[str] = mapped_column('行ラベル', String(20), primary_key=True)
    department_name: Mapped[str] = mapped_column('行名', String(100), nullable=False)
    district_code: Mapped[str] = mapped_column(
        '地区コード', String(20), ForeignKey('district_master.地区コード'), nullable=False
    )
    section_code: Mapped[str] = mapped_column(
        '課コード', String(20), ForeignKey('section_master.課コード'), nullable=False
    )
    agg_section_code: Mapped[str] = mapped_column(
        '集約課コード', String(20), ForeignKey('section_master.課コード'), nullable=False
    )
    kbn_code: Mapped[str] = mapped_column('区分コード', String(20), nullable=False)
    account_code: Mapped[str] = mapped_column(
        '勘定科目コード', String(20), ForeignKey('account_master.勘定科目コード'), nullable=False
    )
    cost_center_code: Mapped[str] = mapped_column(
        '原価センタコード', String(20), ForeignKey('cost_center_master.原価センタコード'), nullable=False
    )

    district: Mapped[DistrictMaster] = relationship()
    section: Mapped[SectionMaster] = relationship(
        foreign_keys='[DepartmentMaster.section_code]'
    )
    agg_section: Mapped[SectionMaster] = relationship(
        foreign_keys='[DepartmentMaster.agg_section_code]'
    )
    account: Mapped[AccountMaster] = relationship()
    cost_center_master_rel: Mapped[CostCenterMaster] = relationship()

    def __repr__(self) -> str:
        return f'<DepartmentMaster {self.department_code} {self.department_name}>'
