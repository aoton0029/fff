from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VKouteiHaifu:
    地区: str
    課コード: str
    工程コード: str
    原価センタ: Optional[str]
    編成: Optional[float]
    固定: Optional[float]
    人員計: Optional[float]
    人員比: Optional[float]
    工程配賦: Optional[float]
    端数調整: float
    工程配賦計: Optional[float]

    @classmethod
    def from_row(cls, row) -> VKouteiHaifu:
        m = row._mapping
        return cls(
            地区=m['地区'],
            課コード=m['課コード'],
            工程コード=m['工程コード'],
            原価センタ=m.get('原価センタ'),
            編成=m.get('編成'),
            固定=m.get('固定'),
            人員計=m.get('人員計'),
            人員比=m.get('人員比'),
            工程配賦=m.get('工程配賦'),
            端数調整=m.get('端数調整', 0),
            工程配賦計=m.get('工程配賦計'),
        )
