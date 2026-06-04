from sqlalchemy import distinct, select

from ..extensions import db
from ..models.dat_ouen import OuenData
from ..models.mst_district import DistrictMaster

# TODO: SQLビュー（v_応援計算）実装後、get_calc_rows をDBクエリに置換
_MOCK_CALC_ROWS = [
    {"district_code": "D01", "section_code": "A01", "process_code": "P001", "from_section": "B02", "to_section": "A01", "days": 5.0, "amount": 300_000},
    {"district_code": "D01", "section_code": "A01", "process_code": "P002", "from_section": "C03", "to_section": "A01", "days": 3.0, "amount": 180_000},
    {"district_code": "D02", "section_code": "B02", "process_code": "P001", "from_section": "A01", "to_section": "B02", "days": 8.0, "amount": 480_000},
    {"district_code": "D02", "section_code": "C03", "process_code": "P003", "from_section": "B02", "to_section": "C03", "days": 2.0, "amount": 120_000},
]


class OuenRepository:
    def get_records_by_batch(self, batch_id: int) -> list[OuenData]:
        return db.session.scalars(
            select(OuenData).filter_by(batch_id=batch_id)
        ).all()

    def get_calc_rows(self) -> list[dict]:
        return _MOCK_CALC_ROWS

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
