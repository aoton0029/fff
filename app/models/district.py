from ..extensions import db


class DistrictMaster(db.Model):
    __tablename__ = 'district_master'

    district_code = db.Column('地区コード', db.String(20), primary_key=True)
    district_name = db.Column('地区名', db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<DistrictMaster {self.district_code} {self.district_name}>'
