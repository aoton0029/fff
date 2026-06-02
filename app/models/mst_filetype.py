from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class FileTypeMaster(db.Model):
    __tablename__ = 'mst_ファイルタイプ'

    filetype_code: Mapped[str] = mapped_column('ファイルタイプコード', String(20), primary_key=True)
    filetype_name: Mapped[str] = mapped_column('ファイルタイプ名', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<FileTypeMaster {self.filetype_code} {self.filetype_name}>'
