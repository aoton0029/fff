from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator


class AllocationRow(BaseModel):
    事業部: str
    地区: str
    課コード: str
    原価区分: str
    工程: str
    日数: float
    工程名: Optional[str] = None
    編成: float
    固定: float

    def to_db_kwargs(self) -> dict:
        return {
            "division_code": self.事業部,
            "district_code": self.地区,
            "section_code": self.課コード,
            "cost_category": self.原価区分,
            "process_code": self.工程,
            "days": self.日数,
            "process_name": self.工程名,
            "formation": self.編成,
            "fixed_count": self.固定,
        }

    @field_validator('事業部', '地区', '課コード', '原価区分', '工程')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('コードは空にできません')
        return v

    @field_validator('日数', '編成', '固定', mode='before')
    @classmethod
    def coerce_numeric(cls, v: object) -> float:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return float(str(v))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @field_validator('工程名', mode='before')
    @classmethod
    def coerce_optional_str(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None
