from sqlalchemy import select

from ..extensions import db
from ..models.dat_labor_transfer import LaborTransferData
from ..models.dat_labor_unit_price import LaborUnitPrice
from ..models.dat_processing_month import ProcessingMonth
from ..models.view_roumuhi_furikae import VRoumuhiFurikae
from .view_queries import ROUMUHI_FURIKAE_SQL


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

    def get_calc_rows(self, unit_price: int = 4134) -> list[VRoumuhiFurikae]:
        result = db.session.execute(ROUMUHI_FURIKAE_SQL, {'unit_price': unit_price})
        return [VRoumuhiFurikae.from_row(row) for row in result]

    def get_current_processing_month(self) -> ProcessingMonth | None:
        return db.session.scalar(select(ProcessingMonth))

    def get_unit_price(self, year_month: str) -> LaborUnitPrice | None:
        return db.session.scalar(
            select(LaborUnitPrice).filter_by(year_month=year_month)
        )
