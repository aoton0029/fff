from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import BaseModel


class ExcelImport(BaseModel, db.Model):
    """Excelファイル取込のメタデータ（ファイル自体は保存しない）"""

    __tablename__ = "excel_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # "imported" | "approved" | "error"
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="imported")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    def __repr__(self) -> str:
        return f"<ExcelImport {self.original_filename} domain={self.domain}>"
