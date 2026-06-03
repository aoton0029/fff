from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class WBSMaster(db.Model):
    __tablename__ = 'mst_WBS'

    wbs_code: Mapped[str] = mapped_column('WBSコード', String(20), primary_key=True)
    wbs_name: Mapped[str] = mapped_column('WBS名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<WBSMaster {self.wbs_code} {self.wbs_name}>'
