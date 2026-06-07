from sqlalchemy import distinct, select

from ..extensions import db
from ..models.dat_ouen import OuenData
from ..models.mst_district import DistrictMaster
from ..models.view_ouen_keisan import VOuenKeisanData
from .view_queries import OUEN_KEISAN_SQL


class OuenRepository:
    def get_records_by_batch(self, batch_id: int, page: int = None, per_page: int = 30,
                             q: str = '', sort: str = 'from_district', order: str = 'asc'):
        col_map = {
            'from_district': OuenData.from_district,
            'from_section_code': OuenData.from_section_code,
            'to_district': OuenData.to_district,
            'to_section_code': OuenData.to_section_code,
        }
        col = col_map.get(sort, OuenData.from_district)
        query = select(OuenData).filter_by(batch_id=batch_id).order_by(
            col.desc() if order == 'desc' else col.asc()
        )
        if q:
            query = query.where(
                OuenData.from_section_code.ilike(f'%{q}%') |
                OuenData.to_section_code.ilike(f'%{q}%')
            )
        if page is None:
            return db.session.scalars(query).all()
        return db.paginate(query, page=page, per_page=per_page, error_out=False)

    def get_calc_rows(self, days_of_month: int = 31) -> list[VOuenKeisanData]:
        result = db.session.execute(OUEN_KEISAN_SQL, {'days_of_month': days_of_month})
        return [VOuenKeisanData.from_row(row) for row in result]

    def get_district_list(self) -> list[dict]:
        district_codes = db.session.scalars(
            select(distinct(OuenData.from_district)).order_by(OuenData.from_district)
        ).all()
        district_map: dict[str, str | None] = {code: None for code in district_codes}
        masters = db.session.scalars(
            select(DistrictMaster).where(DistrictMaster.district_code.in_(district_codes))
        ).all()
        for m in masters:
            district_map[m.district_code] = m.district_name
        return [{"code": code, "name": district_map.get(code)} for code in district_codes]
