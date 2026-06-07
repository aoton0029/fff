from sqlalchemy import select

from ..extensions import db
from ..models.dat_allocation import AllocationData
from ..models.view_koutei_haifu import VKouteiHaifu
from .view_queries import KOUTEI_HAIFU_SQL


class AllocationRepository:
    def get_records_by_batch(self, batch_id: int, page: int = None, per_page: int = 30,
                             q: str = '', sort: str = 'division_code', order: str = 'asc'):
        col_map = {
            'division_code': AllocationData.division_code,
            'district_code': AllocationData.district_code,
            'section_code': AllocationData.section_code,
            'process_code': AllocationData.process_code,
        }
        col = col_map.get(sort, AllocationData.division_code)
        query = select(AllocationData).filter_by(batch_id=batch_id).order_by(
            col.desc() if order == 'desc' else col.asc()
        )
        if q:
            query = query.where(
                AllocationData.division_code.ilike(f'%{q}%') |
                AllocationData.section_code.ilike(f'%{q}%')
            )
        if page is None:
            return db.session.scalars(query).all()
        return db.paginate(query, page=page, per_page=per_page, error_out=False)

    def get_calc_rows(self, days_of_month: int = 31) -> list[VKouteiHaifu]:
        result = db.session.execute(KOUTEI_HAIFU_SQL, {'days_of_month': days_of_month})
        return [VKouteiHaifu.from_row(row) for row in result]
