from datetime import datetime, timezone
from ..extensions import db


class LaborUnitPrice(db.Model):
    __tablename__ = 'labor_unit_prices'

    id = db.Column(db.Integer, primary_key=True)
    year_month = db.Column('年月', db.String(7), nullable=False, unique=True)
    unit_price = db.Column('単価', db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f'<LaborUnitPrice {self.year_month} {self.unit_price}>'
