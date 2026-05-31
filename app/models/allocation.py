from datetime import datetime, timezone
from ..extensions import db


class AllocationData(db.Model):
    __tablename__ = 'allocation_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    division_code = db.Column('事業部', db.String(20), nullable=False)
    district_code = db.Column('地区', db.String(20), nullable=False)
    section_code = db.Column('課コード', db.String(20), nullable=False)
    cost_category = db.Column('原価区分', db.String(20), nullable=False)
    process_code = db.Column('工程', db.String(20), nullable=False)
    days = db.Column('日数', db.Float, nullable=False)
    process_name = db.Column('工程名', db.String(100), nullable=True)
    formation = db.Column('編成', db.Float, nullable=False)
    fixed_count = db.Column('固定', db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='allocation_records', lazy=True)

    def __repr__(self) -> str:
        return f'<AllocationData district={self.district_code} section={self.section_code} process={self.process_code}>'
