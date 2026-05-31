from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator


class LaborTransferRow(BaseModel):
    勘定科目コード: str
    原価センタ: Optional[str] = None
    負担課: Optional[str] = None
    担当課: str
    工事名: Optional[str] = None
    作業時間: float
    WBS: Optional[str] = None
    資産集約番号: Optional[str] = None
    指図: Optional[str] = None
    備考: Optional[str] = None

    @field_validator('勘定科目コード', '担当課')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('コードは空にできません')
        return v

    @field_validator('作業時間', mode='before')
    @classmethod
    def coerce_numeric(cls, v: object) -> float:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return float(str(v))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @field_validator('原価センタ', '負担課', '工事名', 'WBS', '資産集約番号', '指図', '備考', mode='before')
    @classmethod
    def coerce_optional_str(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None
