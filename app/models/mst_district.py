from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class DistrictMaster(db.Model):
    __tablename__ = 'mst_地区'
    __bind_key__ = 'master_db'

    district_code: Mapped[str] = mapped_column('地区コード', String(20), primary_key=True)
    district_name: Mapped[str] = mapped_column('地区名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<DistrictMaster {self.district_code} {self.district_name}>'
