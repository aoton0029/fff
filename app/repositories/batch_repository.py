from sqlalchemy import func, select

from ..extensions import db
from ..models.dat_salary import SalaryData
from ..models.dat_upload_batch import UploadBatch

_PER_PAGE = 20


class UploadBatchRepository:
    def get_paginated(self, file_type: str, page: int, per_page: int = _PER_PAGE):
        query = (
            select(UploadBatch)
            .filter_by(file_type=file_type)
            .order_by(UploadBatch.created_at.desc())
        )
        return db.paginate(query, page=page, per_page=per_page, error_out=False)

    def get_latest(self, file_type: str):
        return db.session.scalar(
            select(UploadBatch)
            .filter_by(file_type=file_type)
            .order_by(UploadBatch.created_at.desc())
        )

    def get_salary_count(self) -> int:
        return db.session.scalar(select(func.count()).select_from(SalaryData))
