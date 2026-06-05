from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class SalaryRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    行ラベル: str
    所属名: Optional[str] = None

    本給: Optional[int] = Field(None, validation_alias='合計 / (明細1)本給')
    能力給: Optional[int] = Field(None, validation_alias='合計 / (明細1)能力給')
    職務役割給: Optional[int] = Field(None, validation_alias='合計 / (明細1)職務・役割給')
    役割業績給: Optional[int] = Field(None, validation_alias='合計 / (明細1)役割業績給')
    報酬: Optional[int] = Field(None, validation_alias='合計 / (明細1)報酬')
    本俸: Optional[int] = Field(None, validation_alias='合計 / (明細1)本俸')
    基本賃金: Optional[int] = Field(None, validation_alias='合計 / (明細1)基本賃金')
    国内給与: Optional[int] = Field(None, validation_alias='合計 / (明細1)国内給与')
    駐在員給与調整: Optional[int] = Field(None, validation_alias='合計 / (明細1)駐在員給与調整')
    家族手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)家族手当')
    資格手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)資格手当')
    交替勤務加算給: Optional[int] = Field(None, validation_alias='合計 / (明細1)交替勤務加算給')
    振替勤務就業手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)振替勤務就業手当')
    早出残業手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)早出残業手当')
    休日出勤手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)休日出勤手当')
    特定休日出勤手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)特定休日出勤手当')
    交替勤務手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)交替勤務手当')
    守衛手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)守衛手当')
    深夜業手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)深夜業手当')
    単身赴任手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)単身赴任手当')
    一時帰省旅費: Optional[int] = Field(None, validation_alias='合計 / (明細1)一時帰省旅費')
    夜間呼出手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)夜間呼出手当')
    出向補償時間: Optional[int] = Field(None, validation_alias='合計 / (明細1)出向補償時間')
    その他手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)その他手当')
    前月育介金額: Optional[int] = Field(None, validation_alias='合計 / (明細1)前月育介金額')
    公的資格手当: Optional[int] = Field(None, validation_alias='合計 / (明細1)公的資格手当')
    賃金控除: Optional[int] = Field(None, validation_alias='合計 / (明細1)賃金控除')
    職場離脱会計: Optional[int] = Field(None, validation_alias='合計 / (明細2)職場離脱(会計)')
    人件費人数会計: Optional[int] = Field(None, validation_alias='合計 / (明細2)人件費人数(会計)')

    def to_db_kwargs(self) -> dict:
        return {
            "row_label": self.行ラベル,
            "section_name": self.所属名,
            "honkyu": self.本給,
            "nouryoku_kyu": self.能力給,
            "shokumu_yakuwari_kyu": self.職務役割給,
            "yakuwari_gyoseki_kyu": self.役割業績給,
            "hoshu": self.報酬,
            "honpo": self.本俸,
            "kihon_chingin": self.基本賃金,
            "kokunai_kyuyo": self.国内給与,
            "chuzaiin_kyuyo_chosei": self.駐在員給与調整,
            "kazoku_teate": self.家族手当,
            "shikaku_teate": self.資格手当,
            "koutai_kinmu_kazan_kyu": self.交替勤務加算給,
            "furikae_kinmu_shugyo_teate": self.振替勤務就業手当,
            "hayade_zangyou_teate": self.早出残業手当,
            "kyujitsu_shukkin_teate": self.休日出勤手当,
            "tokutei_kyujitsu_shukkin_teate": self.特定休日出勤手当,
            "koutai_kinmu_teate": self.交替勤務手当,
            "keibi_teate": self.守衛手当,
            "shinya_teate": self.深夜業手当,
            "tanshin_funin_teate": self.単身赴任手当,
            "ichiji_kisei_ryohi": self.一時帰省旅費,
            "yakan_yobidate_teate": self.夜間呼出手当,
            "shukkou_hoshou_jikan": self.出向補償時間,
            "sonota_teate": self.その他手当,
            "zengetsu_ikukai_kingaku": self.前月育介金額,
            "kouteki_shikaku_teate": self.公的資格手当,
            "chingin_koujyo": self.賃金控除,
            "shokuba_ridatsu_kaikei": self.職場離脱会計,
            "jinkenhi_ninzuu_kaikei": self.人件費人数会計,
        }

    @field_validator('行ラベル')
    @classmethod
    def row_label_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('行ラベルは空にできません')
        return v

    @field_validator('本給', '能力給', '職務役割給', '役割業績給', mode='before')
    @classmethod
    def coerce_required_numeric(cls, v: object) -> int:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @field_validator(
        '報酬', '本俸', '基本賃金', '国内給与', '駐在員給与調整', '家族手当', '資格手当',
        '交替勤務加算給', '振替勤務就業手当', '早出残業手当', '休日出勤手当', '特定休日出勤手当',
        '交替勤務手当', '守衛手当', '深夜業手当', '単身赴任手当', '一時帰省旅費',
        '夜間呼出手当', '出向補償時間', 'その他手当', '前月育介金額', '公的資格手当',
        '賃金控除', '職場離脱会計', '人件費人数会計',
        mode='before',
    )
    @classmethod
    def coerce_optional_numeric(cls, v: object) -> Optional[int]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

