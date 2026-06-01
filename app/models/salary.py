from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .upload_batch import UploadBatch
    from .user import User


class SalaryData(db.Model):
    __tablename__ = 'salary_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey('upload_batches.id'), nullable=False)

    row_label: Mapped[str] = mapped_column('行ラベル', String(20), nullable=False)
    section_name: Mapped[Optional[str]] = mapped_column('所属名', String(100))

    # Extended identifier columns (populated from Excel)
    chiku: Mapped[Optional[str]] = mapped_column('地区', String(20))
    ka_code: Mapped[Optional[str]] = mapped_column('課コード', String(20))
    chiku_ka_code: Mapped[Optional[str]] = mapped_column('地区課コード', String(50))
    shuuyaku_ka_code: Mapped[Optional[str]] = mapped_column('集約課コード', String(20))
    chiku_shuuyaku_ka_code: Mapped[Optional[str]] = mapped_column('地区集約課コード', String(50))
    cost_center: Mapped[Optional[str]] = mapped_column('原価センタ', String(20))
    kubun: Mapped[Optional[str]] = mapped_column('区分', String(20))
    account_subject: Mapped[Optional[str]] = mapped_column('勘定科目', String(20))

    # Required salary columns
    honkyu: Mapped[int] = mapped_column('合計_明細1_本給', Integer, nullable=False)
    nouryoku_kyu: Mapped[int] = mapped_column('合計_明細1_能力給', Integer, nullable=False)
    shokumu_yakuwari_kyu: Mapped[int] = mapped_column('合計_明細1_職務役割給', Integer, nullable=False)
    yakuwari_gyoseki_kyu: Mapped[int] = mapped_column('合計_明細1_役割業績給', Integer, nullable=False)

    # Optional salary columns
    hoshu: Mapped[Optional[int]] = mapped_column('合計_明細1_報酬', Integer)
    honpo: Mapped[Optional[int]] = mapped_column('合計_明細1_本俸', Integer)
    kihon_chingin: Mapped[Optional[int]] = mapped_column('合計_明細1_基本賃金', Integer)
    kokunai_kyuyo: Mapped[Optional[int]] = mapped_column('合計_明細1_国内給与', Integer)
    chuzaiin_kyuyo_chosei: Mapped[Optional[int]] = mapped_column('合計_明細1_駐在員給与調整', Integer)
    kazoku_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_家族手当', Integer)
    shikaku_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_資格手当', Integer)
    koutai_kinmu_kazan_kyu: Mapped[Optional[int]] = mapped_column('合計_明細1_交替勤務加算給', Integer)
    furikae_kinmu_shugyo_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_振替勤務就業手当', Integer)
    hayade_zangyou_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_早出残業手当', Integer)
    kyujitsu_shukkin_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_休日出勤手当', Integer)
    tokutei_kyujitsu_shukkin_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_特定休日出勤手当', Integer)
    koutai_kinmu_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_交替勤務手当', Integer)
    keibi_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_守衛手当', Integer)
    shinya_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_深夜業手当', Integer)
    tanshin_funin_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_単身赴任手当', Integer)
    ichiji_kisei_ryohi: Mapped[Optional[int]] = mapped_column('合計_明細1_一時帰省旅費', Integer)
    yakan_yobidate_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_夜間呼出手当', Integer)
    shukkou_hoshou_jikan: Mapped[Optional[int]] = mapped_column('合計_明細1_出向補償時間', Integer)
    sonota_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_その他手当', Integer)
    zengetsu_ikukai_kingaku: Mapped[Optional[int]] = mapped_column('合計_明細1_前月育介金額', Integer)
    kouteki_shikaku_teate: Mapped[Optional[int]] = mapped_column('合計_明細1_公的資格手当', Integer)
    chingin_koujyo: Mapped[Optional[int]] = mapped_column('合計_明細1_賃金控除', Integer)
    shokuba_ridatsu_kaikei: Mapped[Optional[int]] = mapped_column('合計_明細2_職場離脱会計', Integer)
    jinkenhi_ninzuu_kaikei: Mapped[Optional[int]] = mapped_column('合計_明細2_人件費人数会計', Integer)
    total: Mapped[Optional[int]] = mapped_column('合計', Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='salary_records')
    creator: Mapped[User] = relationship(foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f'<SalaryData row_label={self.row_label}>'
