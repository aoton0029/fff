from sqlalchemy import func, select

from ..extensions import db
from ..models.dat_salary import SalaryData


class SalaryRepository:
    def get_records_by_batch(self, batch_id: int, page: int = None, per_page: int = 30,
                             q: str = '', sort: str = 'row_label', order: str = 'asc'):
        col_map = {
            'row_label': SalaryData.row_label,
            'section_name': SalaryData.section_name,
        }
        col = col_map.get(sort, SalaryData.row_label)
        query = select(SalaryData).filter_by(batch_id=batch_id).order_by(
            col.desc() if order == 'desc' else col.asc()
        )
        if q:
            query = query.where(
                SalaryData.row_label.ilike(f'%{q}%') |
                SalaryData.section_name.ilike(f'%{q}%')
            )
        if page is None:
            return db.session.scalars(query).all()
        return db.paginate(query, page=page, per_page=per_page, error_out=False)

    def count_all(self) -> int:
        return db.session.scalar(select(func.count()).select_from(SalaryData))
