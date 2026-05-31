from datetime import datetime, timezone
from ..extensions import db


class ProcessingMonth(db.Model):
    """月次処理の処理年月を保持するシングルレコードテーブル。"""
    __tablename__ = 'processing_month'

    id = db.Column(db.Integer, primary_key=True)
    year_month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<ProcessingMonth {self.year_month}>'
