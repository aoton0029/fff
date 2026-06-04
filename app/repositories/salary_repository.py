from sqlalchemy import func, select

from ..extensions import db
from ..models.dat_salary import SalaryData


class SalaryRepository:
    def get_records_by_batch(self, batch_id: int) -> list[SalaryData]:
        return db.session.scalars(
            select(SalaryData).filter_by(batch_id=batch_id)
        ).all()

    def count_all(self) -> int:
        return db.session.scalar(select(func.count()).select_from(SalaryData))
