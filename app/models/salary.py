from datetime import datetime, timezone
from typing import Optional
from ..extensions import db


class SalaryData(db.Model):
    __tablename__ = 'salary_data'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=False)

    # String columns
    chiku = db.Column('地区', db.String(50))
    ka_code = db.Column('課コード', db.String(20))
    chiku_ka_code = db.Column('地区_課コード', db.String(50))
    shuuyaku_ka_code = db.Column('集約課コード', db.String(20))
    chiku_shuuyaku_ka_code = db.Column('地区_集約課コード', db.String(50))
    cost_center = db.Column('原価センタ', db.String(20))
    kubun = db.Column('区分', db.String(10))
    account_subject = db.Column('勘定科目', db.String(50))
    row_label = db.Column('行ラベル', db.String(20), nullable=False)
    section_name = db.Column('所属名', db.String(100))

    # Required salary columns
    honkyu = db.Column('合計_明細1_本給', db.Integer, nullable=False)
    nouryoku_kyu = db.Column('合計_明細1_能力給', db.Integer, nullable=False)
    shokumu_yakuwari_kyu = db.Column('合計_明細1_職務役割給', db.Integer, nullable=False)
    yakuwari_gyoseki_kyu = db.Column('合計_明細1_役割業績給', db.Integer, nullable=False)

    # Optional salary columns
    hoshu = db.Column('合計_明細1_報酬', db.Integer)
    honpo = db.Column('合計_明細1_本俸', db.Integer)
    kihon_chingin = db.Column('合計_明細1_基本賃金', db.Integer)
    kokunai_kyuyo = db.Column('合計_明細1_国内給与', db.Integer)
    chuzaiin_kyuyo_chosei = db.Column('合計_明細1_駐在員給与調整', db.Integer)
    kazoku_teate = db.Column('合計_明細1_家族手当', db.Integer)
    shikaku_teate = db.Column('合計_明細1_資格手当', db.Integer)
    koutai_kinmu_kazan_kyu = db.Column('合計_明細1_交替勤務加算給', db.Integer)
    furikae_kinmu_shugyo_teate = db.Column('合計_明細1_振替勤務就業手当', db.Integer)
    hayade_zangyou_teate = db.Column('合計_明細1_早出残業手当', db.Integer)
    kyujitsu_shukkin_teate = db.Column('合計_明細1_休日出勤手当', db.Integer)
    tokutei_kyujitsu_shukkin_teate = db.Column('合計_明細1_特定休日出勤手当', db.Integer)
    koutai_kinmu_teate = db.Column('合計_明細1_交替勤務手当', db.Integer)
    keibi_teate = db.Column('合計_明細1_守衛手当', db.Integer)
    shinya_teate = db.Column('合計_明細1_深夜業手当', db.Integer)
    tanshin_funin_teate = db.Column('合計_明細1_単身赴任手当', db.Integer)
    ichiji_kisei_ryohi = db.Column('合計_明細1_一時帰省旅費', db.Integer)
    yakan_yobidate_teate = db.Column('合計_明細1_夜間呼出手当', db.Integer)
    shukkou_hoshou_jikan = db.Column('合計_明細1_出向補償時間', db.Integer)
    sonota_teate = db.Column('合計_明細1_その他手当', db.Integer)
    zengetsu_ikukai_kingaku = db.Column('合計_明細1_前月育介金額', db.Integer)
    kouteki_shikaku_teate = db.Column('合計_明細1_公的資格手当', db.Integer)
    chingin_koujyo = db.Column('合計_明細1_賃金控除', db.Integer)
    shokuba_ridatsu_kaikei = db.Column('合計_明細2_職場離脱会計', db.Integer)
    jinkenhi_ninzuu_kaikei = db.Column('合計_明細2_人件費人数会計', db.Integer)
    total = db.Column('合計', db.Integer)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    batch = db.relationship('UploadBatch', backref='salary_records', lazy=True)

    def __repr__(self) -> str:
        return f'<SalaryData row_label={self.row_label}>'
