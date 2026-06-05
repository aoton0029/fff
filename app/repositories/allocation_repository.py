from sqlalchemy import select

from ..extensions import db
from ..models.dat_allocation import AllocationData

# TODO: SQLビュー（v_工程配賦計算）実装後、get_calc_rows をDBクエリに置換
_MOCK_CALC_ROWS = [
    {"section_code": "A01", "process_code": "P001", "process_name": "工程A", "formation": 10.0, "fixed_count": 2.0, "days": 20.0, "amount": 1_200_000},
    {"section_code": "A01", "process_code": "P002", "process_name": "工程B", "formation": 8.0,  "fixed_count": 1.0, "days": 18.0, "amount":   980_000},
    {"section_code": "B02", "process_code": "P003", "process_name": "工程C", "formation": 12.0, "fixed_count": 3.0, "days": 22.0, "amount": 1_450_000},
    {"section_code": "B02", "process_code": "P004", "process_name": "工程D", "formation": 6.0,  "fixed_count": 0.0, "days": 15.0, "amount":   670_000},
]


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

    def get_calc_rows(self) -> list[dict]:
        return _MOCK_CALC_ROWS
