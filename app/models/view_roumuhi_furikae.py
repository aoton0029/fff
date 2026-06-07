from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VRoumuhiFurikae:
    勘定科目コード: Optional[str]
    原価センタ: Optional[str]
    負担課: Optional[str]
    担当課: Optional[str]
    工事名: Optional[str]
    作業時間: Optional[float]
    WBS: Optional[str]
    資産集約番号: Optional[str]
    指図: Optional[str]
    備考: Optional[str]
    振替金額: Optional[float]

    @classmethod
    def from_row(cls, row) -> VRoumuhiFurikae:
        m = row._mapping
        return cls(
            勘定科目コード=m.get('勘定科目コード'),
            原価センタ=m.get('原価センタ'),
            負担課=m.get('負担課'),
            担当課=m.get('担当課'),
            工事名=m.get('工事名'),
            作業時間=m.get('作業時間'),
            WBS=m.get('WBS'),
            資産集約番号=m.get('資産集約番号'),
            指図=m.get('指図'),
            備考=m.get('備考'),
            振替金額=m.get('振替金額'),
        )
