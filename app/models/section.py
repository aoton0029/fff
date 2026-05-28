from ..extensions import db


class SectionMaster(db.Model):
    __tablename__ = 'section_master'

    section_code = db.Column('課コード', db.String(20), primary_key=True)
    section_name = db.Column('課名', db.String(100), nullable=False)
    district_code = db.Column('地区コード', db.String(20), nullable=False)
    cost_center_code = db.Column('原価センタコード', db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f'<SectionMaster {self.section_code} {self.section_name}>'
