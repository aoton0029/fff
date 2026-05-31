from datetime import datetime, date as date_type
from typing import Optional

from pydantic import BaseModel, field_validator


class OuenRow(BaseModel):
    送り出し地区: str
    送り出し課コード: str
    受け入れ地区: str
    受け入れ課コード: str
    出課日: Optional[date_type] = None
    帰課日: Optional[date_type] = None
    日数: int
    延日数: int
    備考: Optional[str] = None

    @field_validator('送り出し地区', '送り出し課コード', '受け入れ地区', '受け入れ課コード')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('コードは空にできません')
        return v

    @field_validator('出課日', '帰課日', mode='before')
    @classmethod
    def coerce_date(cls, v: object) -> Optional[date_type]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date_type):
            return v
        try:
            from openpyxl.utils.datetime import from_excel
            result = from_excel(float(str(v)))
            if isinstance(result, datetime):
                return result.date()
            return result
        except Exception:
            raise ValueError(f'日付に変換できません: {v!r}')

    @field_validator('日数', '延日数', mode='before')
    @classmethod
    def coerce_int(cls, v: object) -> int:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @field_validator('備考', mode='before')
    @classmethod
    def coerce_str_optional(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        return str(v).strip() or None
