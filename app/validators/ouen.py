from datetime import datetime, date as date_type
from typing import Optional

from pydantic import BaseModel, field_validator


class OuenRow(BaseModel):
    課コード: int
    課名: Optional[str] = None
    課コード_2: int
    課名_2: Optional[str] = None
    人数: int
    出課日: Optional[date_type] = None
    帰課日: Optional[date_type] = None
    日数: int
    延日数: int
    氏名: Optional[str] = None

    def to_db_kwargs(self) -> dict:
        return {
            "from_section_code": self.課コード,
            "to_section_code": self.課コード_2,
            "departure_date": self.出課日,
            "return_date": self.帰課日,
            "days": self.日数,
            "extended_days": self.延日数,
            "note": self.氏名,
        }

    @field_validator('課コード', '課コード_2')
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

    @field_validator('人数', '日数', '延日数', mode='before')
    @classmethod
    def coerce_int(cls, v: object) -> int:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @field_validator('課名', '課名_2', '氏名', mode='before')
    @classmethod
    def coerce_str_optional(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        return str(v).strip() or None
