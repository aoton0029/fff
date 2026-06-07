from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VOuenKeisanData:
    地区: str
    課コード: str
    区分: Optional[str]
    課コード名: Optional[str]
    応援単価: Optional[float]
    集約課コード: Optional[str]
    送出金額: float
    送出人員数: float
    受入金額: float
    受入人員数: float
    応援後人件費: float
    応援後人員数: float

    @classmethod
    def from_row(cls, row) -> VOuenKeisanData:
        m = row._mapping
        return cls(
            地区=m['地区'],
            課コード=m['課コード'],
            区分=m.get('区分'),
            課コード名=m.get('課コード名'),
            応援単価=m.get('応援単価'),
            集約課コード=m.get('集約課コード'),
            送出金額=m['送出金額'],
            送出人員数=m['送出人員数'],
            受入金額=m['受入金額'],
            受入人員数=m['受入人員数'],
            応援後人件費=m['応援後人件費'],
            応援後人員数=m['応援後人員数'],
        )
