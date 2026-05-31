from ..extensions import db


class CostCenterMaster(db.Model):
    __tablename__ = 'cost_center_master'

    cost_center_code = db.Column('原価センタコード', db.String(20), primary_key=True)
    cost_center_name = db.Column('原価センタ名', db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<CostCenterMaster {self.cost_center_code} {self.cost_center_name}>'
