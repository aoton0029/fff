from ..extensions import db


class DepartmentMaster(db.Model):
    __tablename__ = 'department_master'

    department_code = db.Column('部署コード', db.String(20), primary_key=True)
    department_name = db.Column('部署名', db.String(100), nullable=False)
    district_code = db.Column('地区コード', db.String(20), nullable=False)
    section_code = db.Column('課コード', db.String(20), nullable=False)
    account_code = db.Column('勘定科目コード', db.String(20), nullable=False)
    cost_center_code = db.Column('原価センタコード', db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f'<DepartmentMaster {self.department_code} {self.department_name}>'
