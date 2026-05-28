from pydantic import BaseModel, field_validator


class LaborTransferRow(BaseModel):
    勘定科目コード: str
    from課コード: str
    to課コード: str
    作業時間: float

    @field_validator('勘定科目コード', 'from課コード', 'to課コード')
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
