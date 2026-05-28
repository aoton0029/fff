from pydantic import BaseModel, field_validator, model_validator


class SalaryRow(BaseModel):
    部署コード: str
    本給: int
    能力給: int
    報酬: int
    手当: int
    人員数: int
    給与額: int

    @field_validator('部署コード')
    @classmethod
    def department_code_not_empty(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError('部署コードは空にできません')
        return v

    @field_validator('本給', '能力給', '報酬', '手当', '人員数', '給与額', mode='before')
    @classmethod
    def coerce_numeric(cls, v: object) -> int:
        if isinstance(v, str):
            v = v.replace(',', '').strip()
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            raise ValueError(f'数値に変換できません: {v!r}')

    @model_validator(mode='after')
    def non_negative(self) -> 'SalaryRow':
        for field in ('本給', '能力給', '報酬', '手当', '人員数', '給与額'):
            val = getattr(self, field)
            if val < 0:
                raise ValueError(f'{field}は0以上の値を入力してください')
        return self
