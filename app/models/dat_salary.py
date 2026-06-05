from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .mst_department import DepartmentMaster
    from .dat_upload_batch import UploadBatch
    from .mst_user import User


class SalaryData(db.Model):
    __tablename__ = 'dat_人事給与データ'

    row_label: Mapped[str] = mapped_column('行ラベル', String(20), comment="", primary_key=True)
    section_name: Mapped[Optional[str]] = mapped_column('所属名', String(100))

    batch_id: Mapped[int] = mapped_column(ForeignKey('dat_ファイル.id'), nullable=False)

    honkyu: Mapped[int] = mapped_column('合計_明細1_本給', Integer, nullable=False)
    nouryoku_kyu: Mapped[int] = mapped_column('合計_明細1_能力給', Integer, nullable=False)
    shokumu_yakuwari_kyu: Mapped[int] = mapped_column('合計_明細1_職務役割給', Integer, nullable=False)
    yakuwari_gyoseki_kyu: Mapped[int] = mapped_column('合計_明細1_役割業績給', Integer, nullable=False)
    hoshu: Mapped[int] = mapped_column('合計_明細1_報酬', Integer, nullable=False)
    honpo: Mapped[int] = mapped_column('合計_明細1_本俸', Integer, nullable=False)
    kihon_chingin: Mapped[int] = mapped_column('合計_明細1_基本賃金', Integer, nullable=False)
    kokunai_kyuyo: Mapped[int] = mapped_column('合計_明細1_国内給与', Integer, nullable=False)
    chuzaiin_kyuyo_chosei: Mapped[int] = mapped_column('合計_明細1_駐在員給与調整', Integer, nullable=False)
    kazoku_teate: Mapped[int] = mapped_column('合計_明細1_家族手当', Integer, nullable=False)
    shikaku_teate: Mapped[int] = mapped_column('合計_明細1_資格手当', Integer, nullable=False)
    koutai_kinmu_kazan_kyu: Mapped[int] = mapped_column('合計_明細1_交替勤務加算給', Integer, nullable=False)
    furikae_kinmu_shugyo_teate: Mapped[int] = mapped_column('合計_明細1_振替勤務就業手当', Integer, nullable=False)
    hayade_zangyou_teate: Mapped[int] = mapped_column('合計_明細1_早出残業手当', Integer, nullable=False)
    kyujitsu_shukkin_teate: Mapped[int] = mapped_column('合計_明細1_休日出勤手当', Integer, nullable=False)
    tokutei_kyujitsu_shukkin_teate: Mapped[int] = mapped_column('合計_明細1_特定休日出勤手当', Integer, nullable=False)
    koutai_kinmu_teate: Mapped[int] = mapped_column('合計_明細1_交替勤務手当', Integer, nullable=False)
    keibi_teate: Mapped[int] = mapped_column('合計_明細1_守衛手当', Integer, nullable=False)
    shinya_teate: Mapped[int] = mapped_column('合計_明細1_深夜業手当', Integer, nullable=False)
    tanshin_funin_teate: Mapped[int] = mapped_column('合計_明細1_単身赴任手当', Integer, nullable=False)
    ichiji_kisei_ryohi: Mapped[int] = mapped_column('合計_明細1_一時帰省旅費', Integer, nullable=False)
    yakan_yobidate_teate: Mapped[int] = mapped_column('合計_明細1_夜間呼出手当', Integer, nullable=False)
    shukkou_hoshou_jikan: Mapped[int] = mapped_column('合計_明細1_出向補償時間', Integer, nullable=False)
    sonota_teate: Mapped[int] = mapped_column('合計_明細1_その他手当', Integer, nullable=False)
    zengetsu_ikukai_kingaku: Mapped[int] = mapped_column('合計_明細1_前月育介金額', Integer, nullable=False)
    kouteki_shikaku_teate: Mapped[int] = mapped_column('合計_明細1_公的資格手当', Integer, nullable=False)
    chingin_koujyo: Mapped[int] = mapped_column('合計_明細1_賃金控除', Integer, nullable=False)
    shokuba_ridatsu_kaikei: Mapped[int] = mapped_column('合計_明細2_職場離脱会計', Integer, nullable=False)
    jinkenhi_ninzuu_kaikei: Mapped[int] = mapped_column('合計_明細2_人件費人数会計', Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    batch: Mapped[UploadBatch] = relationship(back_populates='salary_records')
    creator: Mapped[User] = relationship('User', foreign_keys=[created_by], viewonly=True)

    @property
    def total_meisai1(self) -> int:
        cols = [
            self.honkyu, self.nouryoku_kyu, self.shokumu_yakuwari_kyu,
            self.yakuwari_gyoseki_kyu, self.hoshu, self.honpo,
            self.kihon_chingin, self.kokunai_kyuyo, self.chuzaiin_kyuyo_chosei,
            self.kazoku_teate, self.shikaku_teate, self.koutai_kinmu_kazan_kyu,
            self.furikae_kinmu_shugyo_teate, self.hayade_zangyou_teate,
            self.kyujitsu_shukkin_teate, self.tokutei_kyujitsu_shukkin_teate,
            self.koutai_kinmu_teate, self.keibi_teate, self.shinya_teate,
            self.tanshin_funin_teate, self.ichiji_kisei_ryohi,
            self.yakan_yobidate_teate, self.shukkou_hoshou_jikan,
            self.sonota_teate, self.zengetsu_ikukai_kingaku,
            self.kouteki_shikaku_teate, self.chingin_koujyo,
        ]
        return sum(v for v in cols if v is not None)

    @property
    def total_meisai2(self) -> int:
        cols = [
            self.shokuba_ridatsu_kaikei,
            self.jinkenhi_ninzuu_kaikei,
        ]
        return sum(v for v in cols if v is not None)

    @property
    def total(self) -> int:
        return self.total_meisai1 + self.total_meisai2

    @property
    def chiku_ka_code(self) -> Optional[str]:
        return f'{self.district_code}+{self.section_code}'

    @property
    def chiku_shuuyaku_ka_code(self) -> Optional[str]:
        return f'{self.district_code}+{self.agg_section_code}'

    def __repr__(self) -> str:
        return f'<SalaryData row_label={self.row_label}>'
