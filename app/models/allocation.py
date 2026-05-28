from datetime import datetime, timezone
from ..extensions import db


class AllocationData(db.Model):
    __tablename__ = 'allocation_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    district_code = db.Column('地区コード', db.String(20), nullable=False)
    section_code = db.Column('課コード', db.String(20), nullable=False)
    allocation_ratio = db.Column('按分人員数', db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='allocation_records', lazy=True)

    def __repr__(self) -> str:
        return f'<AllocationData district={self.district_code} section={self.section_code}>'
