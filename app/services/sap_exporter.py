"""SAP インターフェース形式テキストファイル生成."""
from __future__ import annotations

import io
from collections import defaultdict

from sqlalchemy import select

from ..extensions import db
from ..models.allocation import AllocationData
from ..models.labor_transfer import LaborTransferData
from ..models.ouen import OuenData
from ..models.salary import SalaryData
from ..models.section import SectionMaster


def build_allocation_tsv() -> bytes:
    """V_工程配賦 相当の計算を行い TSV (cp932 CRLF) を返す。

    計算手順:
      1. V_人事データ   : SalaryData を (地区, 課コード) でグループ集計
      2. V_応援連絡票   : OuenData × 応援単価 → 応援金額
      3. V_応援計算データ: (地区, 集約課コード) 単位で応援後人件費を算出
      4. V_工程配賦     : AllocationData の人員比から工程配賦を計算
    """
    # ── Step 1: V_人事データ ──────────────────────────────────────
    jinjidata: dict[tuple[str, str], dict] = {}
    for r in db.session.scalars(select(SalaryData)).all():
        chiku = r.chiku or ''
        ka = r.ka_code or ''
        if not chiku or not ka:
            continue
        key = (chiku, ka)
        if key not in jinjidata:
            jinjidata[key] = {
                'total': 0,
                'ninzuu': 0,
                'shuuyaku': r.shuuyaku_ka_code or ka,
                'oen_tanka': 0.0,
            }
        e = jinjidata[key]
        e['total'] += r.total or 0
        e['ninzuu'] += r.jinkenhi_ninzuu_kaikei or 0
        if r.shuuyaku_ka_code:
            e['shuuyaku'] = r.shuuyaku_ka_code

    # 応援単価を計算: SUM(合計) / SUM(人件費人数) / 31
    for e in jinjidata.values():
        ninzuu = e['ninzuu']
        e['oen_tanka'] = (e['total'] / ninzuu / 31) if ninzuu else 0.0

    # (地区, 課コード) → 集約課コード マップ
    ka_to_shuuyaku: dict[tuple[str, str], str] = {
        k: e['shuuyaku'] for k, e in jinjidata.items()
    }

    # ── Step 2 & 3: V_応援連絡票 + V_応援計算データ ───────────────
    # 初期値: 各 (地区, 集約課コード) の合計給与
    oen_go: dict[tuple[str, str], float] = defaultdict(float)
    for (chiku, ka), e in jinjidata.items():
        shuuyaku = ka_to_shuuyaku.get((chiku, ka), ka)
        oen_go[(chiku, shuuyaku)] += e['total']

    # 応援の送出 (マイナス) / 受入 (プラス) を反映
    for o in db.session.scalars(select(OuenData)).all():
        from_key = (o.from_district, o.from_section_code)
        tanka = jinjidata.get(from_key, {}).get('oen_tanka', 0.0)
        kinko = tanka * (o.extended_days or 0)

        from_shuuyaku = ka_to_shuuyaku.get(from_key, o.from_section_code)
        oen_go[(o.from_district, from_shuuyaku)] -= kinko

        to_key = (o.to_district, o.to_section_code)
        to_shuuyaku = ka_to_shuuyaku.get(to_key, o.to_section_code)
        oen_go[(o.to_district, to_shuuyaku)] += kinko

    # ── Step 4: V_工程配賦 ───────────────────────────────────────
    # 課コード → 原価センタ マップ (SectionMaster で代用)
    section_cc: dict[str, str] = {
        s.section_code: s.cost_center_code for s in db.session.scalars(select(SectionMaster)).all()
    }

    # 人員計を計算し、(地区, 集約課コード) 単位で合計
    items = []
    jinko_sum: dict[tuple[str, str], float] = defaultdict(float)
    for r in db.session.scalars(select(AllocationData)).all():
        jinko = (r.formation or 0.0) + (r.fixed_count or 0.0)
        shuuyaku = ka_to_shuuyaku.get((r.district_code, r.section_code), r.section_code)
        items.append({'r': r, 'jinko': jinko, 'shuuyaku': shuuyaku})
        jinko_sum[(r.district_code, shuuyaku)] += jinko

    headers = ['地区', '課コード', '工程コード', '原価センタ', '編成', '固定',
               '人員計', '人員比', '工程配賦', '端数調整', '工程配賦計']
    rows: list[list] = [headers]

    for item in items:
        r = item['r']
        jinko = item['jinko']
        shuuyaku = item['shuuyaku']
        total_jinko = jinko_sum[(r.district_code, shuuyaku)]
        jinko_hi = (jinko / total_jinko) if total_jinko else 0.0
        koutei_haibun = round(oen_go.get((r.district_code, shuuyaku), 0.0) * jinko_hi, 0)
        rows.append([
            r.district_code,
            r.section_code,
            r.process_code,
            section_cc.get(r.section_code, ''),
            r.formation,
            r.fixed_count,
            jinko,
            round(jinko_hi, 6),
            int(koutei_haibun),
            0,
            int(koutei_haibun),
        ])

    return _to_tsv_bytes(rows)


def build_labor_tsv(unit_price: float) -> bytes:
    """V_労務費振替依頼書 相当の TSV (cp932 CRLF) を返す。

    振替金額 = ROUND(作業時間 × unit_price, 0)
    """
    headers = ['勘定科目コード', '原価センタ', '負担課', '担当課', '工事名',
               '作業時間', '振替金額', 'WBS', '資産集約番号', '指図', '備考']
    rows: list[list] = [headers]

    for r in db.session.scalars(select(LaborTransferData)).all():
        furikae = round((r.work_hours or 0.0) * unit_price, 0)
        rows.append([
            r.account_code,
            r.cost_center or '',
            r.burden_section or '',
            r.charge_section,
            r.construction_name or '',
            r.work_hours,
            int(furikae),
            r.wbs or '',
            r.asset_number or '',
            r.order_number or '',
            r.note or '',
        ])

    return _to_tsv_bytes(rows)


def _to_tsv_bytes(rows: list[list]) -> bytes:
    """行リストをタブ区切り・CRLF・cp932 のバイト列に変換する。"""
    buf = io.StringIO()
    for row in rows:
        buf.write('\t'.join(str(v) for v in row) + '\r\n')
    return buf.getvalue().encode('cp932', errors='replace')
