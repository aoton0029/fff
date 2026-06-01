from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class SalaryRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    行ラベル: str
    所属名: Optional[str] = None

    # Required salary columns
    本給: int = Field(validation_alias='合計/(明細1)本給')
    能力給: int = Field(validation_alias='合計/(明細1)能力給')
    職務役割給: int = Field(validation_alias='合計/(明細1)職務・役割給')
    役割業績給: int = Field(validation_alias='合計/(明細1)役割業績給')

    # Optional salary columns
    報酬: Optional[int] = Field(None, validation_alias='合計/(明細1)報酬')
    本俸: Optional[int] = Field(None, validation_alias='合計/(明細1)本俸')
    基本賃金: Optional[int] = Field(None, validation_alias='合計/(明細1)基本賃金')
    国内給与: Optional[int] = Field(None, validation_alias='合計/(明細1)国内給与')
    駐在員給与調整: Optional[int] = Field(None, validation_alias='合計/(明細1)駐在員給与調整')
    家族手当: Optional[int] = Field(None, validation_alias='合計/(明細1)家族手当')
    資格手当: Optional[int] = Field(None, validation_alias='合計/(明細1)資格手当')
    交替勤務加算給: Optional[int] = Field(None, validation_alias='合計/(明細1)交替勤務加算給')
    振替勤務就業手当: Optional[int] = Field(None, validation_alias='合計/(明細1)振替勤務就業手当')
    早出残業手当: Optional[int] = Field(None, validation_alias='合計/(明細1)早出残業手当')
    休日出勤手当: Optional[int] = Field(None, validation_alias='合計/(明細1)休日出勤手当')
    特定休日出勤手当: Optional[int] = Field(None, validation_alias='合計/(明細1)特定休日出勤手当')
    交替勤務手当: Optional[int] = Field(None, validation_alias='合計/(明細1)交替勤務手当')
    守衛手当: Optional[int] = Field(None, validation_alias='合計/(明細1)守衛手当')
    深夜業手当: Optional[int] = Field(None, validation_alias='合計/(明細1)深夜業手当')
    単身赴任手当: Optional[int] = Field(None, validation_alias='合計/(明細1)単身赴任手当')
    一時帰省旅費: Optional[int] = Field(None, validation_alias='合計/(明細1)一時帰省旅費')
    夜間呼出手当: Optional[int] = Field(None, validation_alias='合計/(明細1)夜間呼出手当')
    出向補償時間: Optional[int] = Field(None, validation_alias='合計/(明細1)出向補償時間')
    その他手当: Optional[int] = Field(None, validation_alias='合計/(明細1)その他手当')
    前月育介金額: Optional[int] = Field(None, validation_alias='合計/(明細1)前月育介金額')
    公的資格手当: Optional[int] = Field(None, validation_alias='合計/(明細1)公的資格手当')
    賃金控除: Optional[int] = Field(None, validation_alias='合計/(明細1)賃金控除')
    職場離脱会計: Optional[int] = Field(None, validation_alias='合計/(明細2)職場離脱(会計)')
    人件費人数会計: Optional[int] = Field(None, validation_alias='合計/(明細2)人件費人数(会計)')
    合計: Optional[int] = None

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
        '賃金控除', '職場離脱会計', '人件費人数会計', '合計',
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

