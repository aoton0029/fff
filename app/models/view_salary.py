from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VSalaryData:
    地区: str
    課コード: str
    集約課コード: Optional[str]
    原価センタ: Optional[str]
    区分: Optional[str]
    勘定科目: Optional[str]
    応援単価: Optional[float]
    合計: Optional[int]
    人員数: Optional[int]

    @classmethod
    def from_row(cls, row) -> VSalaryData:
        m = row._mapping
        return cls(
            地区=m['地区コード'],
            課コード=m['課コード'],
            集約課コード=m.get('集約課コード'),
            原価センタ=m.get('原価センタ'),
            区分=m.get('区分'),
            勘定科目=m.get('勘定科目'),
            応援単価=m.get('応援単価'),
            合計=m.get('合計'),
            人員数=m.get('人員数'),
        )
