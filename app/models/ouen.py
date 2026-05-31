from datetime import datetime, timezone
from ..extensions import db


class OuenData(db.Model):
    __tablename__ = 'ouen_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)
    from_district = db.Column(db.String(20), nullable=False)
    from_section_code = db.Column(db.String(20), nullable=False)
    to_district = db.Column(db.String(20), nullable=False)
    to_section_code = db.Column(db.String(20), nullable=False)
    departure_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.Date, nullable=True)
    days = db.Column(db.Integer, nullable=False)
    extended_days = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='ouen_records', lazy=True)

    def __repr__(self) -> str:
        return f'<OuenData from={self.from_section_code} to={self.to_section_code}>'
