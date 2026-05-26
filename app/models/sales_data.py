from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import BaseModel


class SalesData(BaseModel, db.Model):
    """ドメイン 'sales' の取込データ行（売上データ）"""

    __tablename__ = "sales_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    import_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("excel_imports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[str | None] = mapped_column(String(100), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    def __repr__(self) -> str:
        return f"<SalesData import_id={self.import_id} product={self.product}>"
