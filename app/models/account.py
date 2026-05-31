from ..extensions import db


class AccountMaster(db.Model):
    __tablename__ = 'account_master'

    account_code = db.Column('勘定科目コード', db.String(20), primary_key=True)
    account_name = db.Column('勘定科目名', db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<AccountMaster {self.account_code} {self.account_name}>'
