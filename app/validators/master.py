"""Pydantic validators for section master and department master import."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

_MAX_CODE = 20
_MAX_NAME = 100
_MAX_KBN = 20


def _require(v: object, label: str, max_len: int) -> str:
    s = str(v).strip() if v is not None else ''
    if not s:
        raise ValueError(f'{label} は必須です')
    if len(s) > max_len:
        raise ValueError(f'{label} は{max_len}文字以内で入力してください')
    return s


class SectionMasterRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    section_code: str
    section_name: str
    district_code: str
    cost_center_code: str

    @field_validator('section_code', mode='before')
    @classmethod
    def v_section_code(cls, v: object) -> str:
        return _require(v, 'section_code', _MAX_CODE)

    @field_validator('section_name', mode='before')
    @classmethod
    def v_section_name(cls, v: object) -> str:
        return _require(v, 'section_name', _MAX_NAME)

    @field_validator('district_code', mode='before')
    @classmethod
    def v_district_code(cls, v: object) -> str:
        return _require(v, 'district_code', _MAX_CODE)

    @field_validator('cost_center_code', mode='before')
    @classmethod
    def v_cost_center_code(cls, v: object) -> str:
        return _require(v, 'cost_center_code', _MAX_CODE)


class DepartmentMasterRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    department_code: str
    department_name: str
    district_code: str
    section_code: str
    agg_section_code: str
    kbn_code: str
    account_code: str
    cost_center_code: str

    @field_validator('department_code', mode='before')
    @classmethod
    def v_department_code(cls, v: object) -> str:
        return _require(v, 'department_code', _MAX_CODE)

    @field_validator('department_name', mode='before')
    @classmethod
    def v_department_name(cls, v: object) -> str:
        return _require(v, 'department_name', _MAX_NAME)

    @field_validator('district_code', mode='before')
    @classmethod
    def v_district_code(cls, v: object) -> str:
        return _require(v, 'district_code', _MAX_CODE)

    @field_validator('section_code', mode='before')
    @classmethod
    def v_section_code(cls, v: object) -> str:
        return _require(v, 'section_code', _MAX_CODE)

    @field_validator('agg_section_code', mode='before')
    @classmethod
    def v_agg_section_code(cls, v: object) -> str:
        return _require(v, 'agg_section_code', _MAX_CODE)

    @field_validator('kbn_code', mode='before')
    @classmethod
    def v_kbn_code(cls, v: object) -> str:
        return _require(v, 'kbn_code', _MAX_KBN)

    @field_validator('account_code', mode='before')
    @classmethod
    def v_account_code(cls, v: object) -> str:
        return _require(v, 'account_code', _MAX_CODE)

    @field_validator('cost_center_code', mode='before')
    @classmethod
    def v_cost_center_code(cls, v: object) -> str:
        return _require(v, 'cost_center_code', _MAX_CODE)
