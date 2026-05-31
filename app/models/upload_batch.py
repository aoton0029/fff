from datetime import datetime, timezone
from ..extensions import db


class UploadBatch(db.Model):
    __tablename__ = 'upload_batches'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # salary / allocation / labor_transfer
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_count = db.Column(db.Integer, default=0, nullable=False)

    creator = db.relationship('User', backref='upload_batches', lazy=True)

    def __repr__(self) -> str:
        return f'<UploadBatch {self.file_name} ({self.file_type})>'
