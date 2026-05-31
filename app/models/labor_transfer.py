from datetime import datetime, timezone
from ..extensions import db


class LaborTransferData(db.Model):
    __tablename__ = 'labor_transfer_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    account_code = db.Column('勘定科目コード', db.String(30), nullable=False)
    cost_center = db.Column('原価センタ', db.String(30), nullable=True)
    burden_section = db.Column('負担課', db.String(30), nullable=True)
    charge_section = db.Column('担当課', db.String(30), nullable=False)
    construction_name = db.Column('工事名', db.String(200), nullable=True)
    work_hours = db.Column('作業時間', db.Float, nullable=False)
    wbs = db.Column('WBS', db.String(100), nullable=True)
    asset_number = db.Column('資産集約番号', db.String(50), nullable=True)
    order_number = db.Column('指図', db.String(50), nullable=True)
    note = db.Column('備考', db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='labor_transfer_records', lazy=True)

    def __repr__(self) -> str:
        return f'<LaborTransferData account={self.account_code} charge={self.charge_section}>'
