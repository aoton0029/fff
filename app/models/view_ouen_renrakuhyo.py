from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VOuenRenrakuhyo:
    送り出し_地区: str
    送り出し_課コード: str
    受け入れ_地区: str
    受け入れ_課コード: str
    応援延日数: Optional[int]
    応援単価: Optional[float]
    応援人員: Optional[float]
    応援金額: Optional[float]

    @classmethod
    def from_row(cls, row) -> VOuenRenrakuhyo:
        m = row._mapping
        return cls(
            送り出し_地区=m['送り出し_地区'],
            送り出し_課コード=m['送り出し_課コード'],
            受け入れ_地区=m['受け入れ_地区'],
            受け入れ_課コード=m['受け入れ_課コード'],
            応援延日数=m.get('応援延日数'),
            応援単価=m.get('応援単価'),
            応援人員=m.get('応援人員'),
            応援金額=m.get('応援金額'),
        )
