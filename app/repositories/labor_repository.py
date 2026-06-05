from sqlalchemy import select

from ..extensions import db
from ..models.dat_labor_transfer import LaborTransferData
from ..models.dat_labor_unit_price import LaborUnitPrice
from ..models.dat_processing_month import ProcessingMonth

# TODO: SQLビュー（v_労務費計算）実装後、get_calc_rows をDBクエリに置換
_MOCK_CALC_ROWS = [
    {"section_code": "A01", "transfer_code": "T001", "transfer_kbn": "振替", "hours": 160.0, "unit_price": 2500.0, "amount": 400_000},
    {"section_code": "A01", "transfer_code": "T002", "transfer_kbn": "振替", "hours": 80.0,  "unit_price": 2500.0, "amount": 200_000},
    {"section_code": "B02", "transfer_code": "T003", "transfer_kbn": "振替", "hours": 200.0, "unit_price": 2800.0, "amount": 560_000},
    {"section_code": "C03", "transfer_code": "T004", "transfer_kbn": "振替", "hours": 120.0, "unit_price": 3000.0, "amount": 360_000},
]


class LaborRepository:
    def get_records_by_batch(self, batch_id: int, page: int = None, per_page: int = 30,
                             q: str = '', sort: str = 'account_code', order: str = 'asc'):
        col_map = {
            'account_code': LaborTransferData.account_code,
            'cost_center': LaborTransferData.cost_center,
            'burden_section': LaborTransferData.burden_section,
            'charge_section': LaborTransferData.charge_section,
        }
        col = col_map.get(sort, LaborTransferData.account_code)
        query = select(LaborTransferData).filter_by(batch_id=batch_id).order_by(
            col.desc() if order == 'desc' else col.asc()
        )
        if q:
            query = query.where(
                LaborTransferData.account_code.ilike(f'%{q}%') |
                LaborTransferData.charge_section.ilike(f'%{q}%')
            )
        if page is None:
            return db.session.scalars(query).all()
        return db.paginate(query, page=page, per_page=per_page, error_out=False)

    def get_calc_rows(self) -> list[dict]:
        return _MOCK_CALC_ROWS

    def get_current_processing_month(self) -> ProcessingMonth | None:
        return db.session.scalar(select(ProcessingMonth))

    def get_unit_price(self, year_month: str) -> LaborUnitPrice | None:
        return db.session.scalar(
            select(LaborUnitPrice).filter_by(year_month=year_month)
        )
