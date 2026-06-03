from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class AccountMaster(db.Model):
    __tablename__ = 'mst_勘定科目'

    account_code: Mapped[str] = mapped_column('勘定科目コード', String(20), primary_key=True)
    account_name: Mapped[str] = mapped_column('勘定科目名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<AccountMaster {self.account_code} {self.account_name}>'
