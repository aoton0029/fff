from pydantic import BaseModel, field_validator


class AllocationRow(BaseModel):
    地区コード: str
    課コード: str
    按分人員数: float

    @field_validator('地区コード', '課コード')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('コードは空にできません')
        return v

    @field_validator('按分人員数', mode='before')
    @classmethod
    def coerce_numeric(cls, v: object) -> float:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return float(str(v))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')
