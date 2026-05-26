from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import BaseModel


class InventoryData(BaseModel, db.Model):
    """ドメイン 'inventory' の取込データ行（在庫管理）"""

    __tablename__ = "inventory_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    import_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("excel_imports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    item_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stock: Mapped[str | None] = mapped_column(String(100), nullable=True)
    warehouse: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    def __repr__(self) -> str:
        return f"<InventoryData import_id={self.import_id} code={self.code}>"
