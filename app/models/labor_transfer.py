from datetime import datetime, timezone
from ..extensions import db


class LaborTransferData(db.Model):
    __tablename__ = 'labor_transfer_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    account_code = db.Column('勘定科目コード', db.String(20), nullable=False)
    from_section_code = db.Column('from課コード', db.String(20), nullable=False)
    to_section_code = db.Column('to課コード', db.String(20), nullable=False)
    work_hours = db.Column('作業時間', db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='labor_transfer_records', lazy=True)

    def __repr__(self) -> str:
        return f'<LaborTransferData from={self.from_section_code} to={self.to_section_code}>'
