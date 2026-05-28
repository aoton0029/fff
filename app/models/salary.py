from datetime import datetime, timezone
from ..extensions import db


class SalaryData(db.Model):
    __tablename__ = 'salary_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    department_code = db.Column('部署コード', db.String(20), nullable=False)
    base_salary = db.Column('本給', db.Integer, nullable=False)
    ability_salary = db.Column('能力給', db.Integer, nullable=False)
    compensation = db.Column('報酬', db.Integer, nullable=False)
    allowance = db.Column('手当', db.Integer, nullable=False)
    headcount = db.Column('人員数', db.Integer, nullable=False)
    total_salary = db.Column('給与額', db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='salary_records', lazy=True)

    def __repr__(self) -> str:
        return f'<SalaryData dept={self.department_code}>'
