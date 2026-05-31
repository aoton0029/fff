"""5 つの SQL ビュー定義に対応する SQLAlchemy ORM クエリ関数群

| SQL ビュー        | ORM 関数                          |
|-------------------|-----------------------------------|
| V_人事データ        | query_v_jinzi_data                |
| V_応援連絡票        | query_v_ouen_renrakuhyo           |
| V_応援計算データ    | query_v_ouen_keisan_data          |
| V_労務費振替依頼書  | query_v_roumuhi_furikae_iraisho   |
| V_工程配賦          | query_v_koutei_haibun             |

各関数は Query オブジェクトを返すため、呼び出し元で .all() / .paginate() 等を使用できる。

スキーマの対応関係（SQL ビューのテーブル → 現モデル）:
  dat_人事データ          → SalaryData          (salary_data)
  dat_応援連絡票          → OuenData            (ouen_data)
  労務費振替依頼書        → LaborTransferData   (labor_transfer_data)
  dat_工程別人員配賦データ → AllocationData      (allocation_data)  ※列構造が異なる
  C1課コードマスタ/変換マスタ → SectionMaster   (section_master)    ※部分的に代替
  SAP原価センタマスタ     → SectionMaster       (cost_center_code 列)
"""

from sqlalchemy import Float, cast, func
from sqlalchemy.orm import aliased

from .extensions import db
from .models.allocation import AllocationData
from .models.labor_transfer import LaborTransferData
from .models.labor_unit_price import LaborUnitPrice
from .models.ouen import OuenData
from .models.salary import SalaryData
from .models.section import SectionMaster


# ---------------------------------------------------------------------------
# V_人事データ
# ---------------------------------------------------------------------------

def query_v_jinzi_data(batch_id: int | None = None):
    """V_人事データ に相当するクエリ。

    salary_data を地区・課コード単位で集計し、応援単価を算出する。
    元 SQL: dat_人事データ を GROUP BY 地区, 課コード

    返却列:
        chiku            … 地区
        ka_code          … 課コード
        shuuyaku_ka_code … 集約課コード (MAX)
        cost_center      … 原価センタ (MAX)
        kubun            … 区分 (MAX)
        account_subject  … 勘定科目 (MAX)
        ouen_tanka       … 応援単価 = SUM(合計) / SUM(人件費人数会計) / 31
        total            … 合計 (SUM)
        ninzuu           … 人員数 = SUM(人件費人数会計)

    Args:
        batch_id: salary の UploadBatch.id。None のとき全バッチが対象。
    """
    q = (
        db.session.query(
            SalaryData.chiku.label('chiku'),
            SalaryData.ka_code.label('ka_code'),
            func.max(SalaryData.shuuyaku_ka_code).label('shuuyaku_ka_code'),
            func.max(SalaryData.cost_center).label('cost_center'),
            func.max(SalaryData.kubun).label('kubun'),
            func.max(SalaryData.account_subject).label('account_subject'),
            (
                cast(func.sum(SalaryData.total), Float)
                / func.sum(SalaryData.jinkenhi_ninzuu_kaikei)
                / 31.0
            ).label('ouen_tanka'),
            func.sum(SalaryData.total).label('total'),
            func.sum(SalaryData.jinkenhi_ninzuu_kaikei).label('ninzuu'),
        )
        .group_by(SalaryData.chiku, SalaryData.ka_code)
    )
    if batch_id is not None:
        q = q.filter(SalaryData.batch_id == batch_id)
    return q


# ---------------------------------------------------------------------------
# V_応援連絡票
# ---------------------------------------------------------------------------

def query_v_ouen_renrakuhyo(
    ouen_batch_id: int | None = None,
    salary_batch_id: int | None = None,
):
    """V_応援連絡票 に相当するクエリ。

    ouen_data に人事データ由来の応援単価と section_master 由来の課名称を結合する。
    元 SQL: dat_応援連絡票 LEFT JOIN (dat_人事データ 集計) ON 送り出し地区+課コード

    返却列:
        okuri_chiku    … 送り出し地区
        okuri_ka_code  … 送り出し課コード
        okuri_ka_name  … 送り出し課名称 (section_master より)
        ukeire_chiku   … 受け入れ地区
        ukeire_ka_code … 受け入れ課コード
        ukeire_ka_name … 受け入れ課名称 (section_master より)
        extended_days  … 応援延日数
        ouen_tanka     … 応援単価 (人事データより)
        ouen_ninzuu    … 応援人員 = ROUND(応援延日数 / 31, 1)
        ouen_kingaku   … 応援金額 = 応援単価 × 応援延日数

    Note:
        元 SQL の 送り出し_課名称 / 受け入れ_課名称 は dat_応援連絡票 の列だが、
        現モデル OuenData にその列がないため section_master を LEFT JOIN で補完する。

    Args:
        ouen_batch_id:   ouen の UploadBatch.id
        salary_batch_id: salary の UploadBatch.id（応援単価算出用）
    """
    salary_sq = query_v_jinzi_data(batch_id=salary_batch_id).subquery('salary_for_ouen')

    FromSection = aliased(SectionMaster, name='from_sec')
    ToSection = aliased(SectionMaster, name='to_sec')

    q = (
        db.session.query(
            OuenData.from_district.label('okuri_chiku'),
            OuenData.from_section_code.label('okuri_ka_code'),
            FromSection.section_name.label('okuri_ka_name'),
            OuenData.to_district.label('ukeire_chiku'),
            OuenData.to_section_code.label('ukeire_ka_code'),
            ToSection.section_name.label('ukeire_ka_name'),
            OuenData.extended_days.label('extended_days'),
            salary_sq.c.ouen_tanka.label('ouen_tanka'),
            func.round(
                cast(OuenData.extended_days, Float) / 31.0, 1
            ).label('ouen_ninzuu'),
            (salary_sq.c.ouen_tanka * OuenData.extended_days).label('ouen_kingaku'),
        )
        .outerjoin(
            FromSection,
            FromSection.section_code == OuenData.from_section_code,
        )
        .outerjoin(
            ToSection,
            ToSection.section_code == OuenData.to_section_code,
        )
        .outerjoin(
            salary_sq,
            (salary_sq.c.chiku == OuenData.from_district)
            & (salary_sq.c.ka_code == OuenData.from_section_code),
        )
    )
    if ouen_batch_id is not None:
        q = q.filter(OuenData.batch_id == ouen_batch_id)
    return q


# ---------------------------------------------------------------------------
# V_応援計算データ
# ---------------------------------------------------------------------------

def query_v_ouen_keisan_data(
    salary_batch_id: int | None = None,
    ouen_batch_id: int | None = None,
):
    """V_応援計算データ に相当するクエリ。

    V_人事データ を基準に V_応援連絡票 の送出・受入金額を加算し、
    応援後人件費・応援後人員数を算出する。
    元 SQL: V_人事データ LEFT JOIN 送出集計 LEFT JOIN 受入集計 LEFT JOIN C1課コードマスタ

    返却列:
        chiku            … 地区
        ka_code          … 課コード
        kubun            … 区分
        ka_name          … 課コード名 (section_master より)
        ouen_tanka       … 応援単価
        shuuyaku_ka_code … 集約課コード
        okuri_kingaku    … 送出金額（負値）
        okuri_ninzuu     … 送出人員数（負値）
        ukeire_kingaku   … 受入金額
        ukeire_ninzuu    … 受入人員数
        ouen_go_jinkenhi … 応援後人件費 = 合計 + 送出金額 + 受入金額
        ouen_go_ninzuu   … 応援後人員数 = 人員数 + 送出人員数 + 受入人員数

    Args:
        salary_batch_id: salary の UploadBatch.id
        ouen_batch_id:   ouen の UploadBatch.id
    """
    jinzi_sq = query_v_jinzi_data(batch_id=salary_batch_id).subquery('jinzi')

    ouen_sq = query_v_ouen_renrakuhyo(
        ouen_batch_id=ouen_batch_id,
        salary_batch_id=salary_batch_id,
    ).subquery('ouen_amounts')

    # 送り出し課ごとに集計（金額・人員はマイナス）
    okuri_sq = (
        db.session.query(
            ouen_sq.c.okuri_chiku,
            ouen_sq.c.okuri_ka_code,
            (-func.sum(ouen_sq.c.ouen_kingaku)).label('okuri_kingaku'),
            (-func.sum(ouen_sq.c.ouen_ninzuu)).label('okuri_ninzuu'),
        )
        .group_by(ouen_sq.c.okuri_chiku, ouen_sq.c.okuri_ka_code)
        .subquery('okuri')
    )

    # 受け入れ課ごとに集計
    ukeire_sq = (
        db.session.query(
            ouen_sq.c.ukeire_chiku,
            ouen_sq.c.ukeire_ka_code,
            func.sum(ouen_sq.c.ouen_kingaku).label('ukeire_kingaku'),
            func.sum(ouen_sq.c.ouen_ninzuu).label('ukeire_ninzuu'),
        )
        .group_by(ouen_sq.c.ukeire_chiku, ouen_sq.c.ukeire_ka_code)
        .subquery('ukeire')
    )

    q = (
        db.session.query(
            jinzi_sq.c.chiku,
            jinzi_sq.c.ka_code,
            jinzi_sq.c.kubun,
            SectionMaster.section_name.label('ka_name'),
            jinzi_sq.c.ouen_tanka,
            jinzi_sq.c.shuuyaku_ka_code,
            func.coalesce(okuri_sq.c.okuri_kingaku, 0).label('okuri_kingaku'),
            func.coalesce(okuri_sq.c.okuri_ninzuu, 0).label('okuri_ninzuu'),
            func.coalesce(ukeire_sq.c.ukeire_kingaku, 0).label('ukeire_kingaku'),
            func.coalesce(ukeire_sq.c.ukeire_ninzuu, 0).label('ukeire_ninzuu'),
            (
                func.coalesce(jinzi_sq.c.total, 0)
                + func.coalesce(okuri_sq.c.okuri_kingaku, 0)
                + func.coalesce(ukeire_sq.c.ukeire_kingaku, 0)
            ).label('ouen_go_jinkenhi'),
            (
                func.coalesce(jinzi_sq.c.ninzuu, 0)
                + func.coalesce(okuri_sq.c.okuri_ninzuu, 0)
                + func.coalesce(ukeire_sq.c.ukeire_ninzuu, 0)
            ).label('ouen_go_ninzuu'),
        )
        .select_from(jinzi_sq)
        .outerjoin(
            okuri_sq,
            (okuri_sq.c.okuri_chiku == jinzi_sq.c.chiku)
            & (okuri_sq.c.okuri_ka_code == jinzi_sq.c.ka_code),
        )
        .outerjoin(
            ukeire_sq,
            (ukeire_sq.c.ukeire_chiku == jinzi_sq.c.chiku)
            & (ukeire_sq.c.ukeire_ka_code == jinzi_sq.c.ka_code),
        )
        .outerjoin(
            SectionMaster,
            SectionMaster.section_code == jinzi_sq.c.ka_code,
        )
    )
    return q


# ---------------------------------------------------------------------------
# V_労務費振替依頼書
# ---------------------------------------------------------------------------

def query_v_roumuhi_furikae_iraisho(
    labor_batch_id: int | None = None,
    year_month: str | None = None,
):
    """V_労務費振替依頼書 に相当するクエリ。

    labor_transfer_data に振替金額（作業時間 × 労務費単価）を付加する。
    元 SQL: 労務費振替依頼書 LEFT JOIN 課コード変換 + ROUND(作業時間 * 4134, 0)

    返却列:
        id                   … LaborTransferData.id
        batch_id             … バッチ ID
        account_code         … 勘定科目コード
        from_section_code    … 振替元課コード
        to_section_code      … 振替先課コード
        work_hours           … 作業時間
        from_section_name    … 振替元課名 (section_master より)
        from_district_code   … 振替元地区コード (section_master より)
        from_cost_center_code … 振替元原価センタコード (section_master より)
        furikae_kingaku      … 振替金額 = ROUND(作業時間 × 単価, 0)

    Note:
        元の SQL は固定値 4134 を単価として使用していたが、本クエリでは
        labor_unit_prices テーブルの単価を参照する。
        元 SQL の 課コード変換 は SectionMaster で代替する（課コードのみで JOIN）。

    Args:
        labor_batch_id: labor_transfer の UploadBatch.id
        year_month:     使用する単価の年月 (例: '2026-05')。
                        None のとき最新登録の単価を使用。
    """
    unit_price_q = db.session.query(LaborUnitPrice.unit_price)
    if year_month is not None:
        unit_price_q = unit_price_q.filter(LaborUnitPrice.year_month == year_month)
    else:
        unit_price_q = unit_price_q.order_by(LaborUnitPrice.year_month.desc()).limit(1)
    unit_price_sq = unit_price_q.scalar_subquery()

    FromSection = aliased(SectionMaster, name='from_sec')

    q = (
        db.session.query(
            LaborTransferData.id,
            LaborTransferData.batch_id,
            LaborTransferData.account_code,
            LaborTransferData.from_section_code,
            LaborTransferData.to_section_code,
            LaborTransferData.work_hours,
            FromSection.section_name.label('from_section_name'),
            FromSection.district_code.label('from_district_code'),
            FromSection.cost_center_code.label('from_cost_center_code'),
            func.round(
                LaborTransferData.work_hours * unit_price_sq, 0
            ).label('furikae_kingaku'),
        )
        .outerjoin(
            FromSection,
            FromSection.section_code == LaborTransferData.from_section_code,
        )
    )
    if labor_batch_id is not None:
        q = q.filter(LaborTransferData.batch_id == labor_batch_id)
    return q


# ---------------------------------------------------------------------------
# V_工程配賦
# ---------------------------------------------------------------------------

def query_v_koutei_haibun(
    salary_batch_id: int | None = None,
    ouen_batch_id: int | None = None,
    allocation_batch_id: int | None = None,
):
    """V_工程配賦 の簡易版クエリ。

    応援後人件費（V_応援計算データ）を配賦データの按分人員数で按分する。
    元 SQL: dat_工程別人員配賦データ × 変換マスタ × SAP原価センタマスタ × V_応援計算データ

    返却列:
        chiku           … 地区コード
        ka_code         … 課コード
        cost_center     … 原価センタコード (section_master より)
        allocation_ratio … 按分人員数
        ninzuu_hi       … 人員比 = 按分人員数 / 課内合計
        koutei_haibun   … 工程配賦 = ROUND(応援後人件費 × 人員比, 0)

    NOTE - スキーマ制約:
        元の dat_工程別人員配賦データ には 工程コード・編成・固定 等の列があるが、
        現在の allocation_data は (地区コード, 課コード, 按分人員数) の 3 列のみ。
        このため工程コード単位の配賦は不可能であり、課コード単位の按分になる。
        変換マスタ（集約課コード取得）・SAP原価センタマスタ は SectionMaster で代替。
        PARTITION BY 集約課コード の WINDOW 関数は課コード単位の GROUP BY で近似する。

    Args:
        salary_batch_id:     salary の UploadBatch.id
        ouen_batch_id:       ouen の UploadBatch.id
        allocation_batch_id: allocation の UploadBatch.id
    """
    ouen_keisan_sq = query_v_ouen_keisan_data(
        salary_batch_id=salary_batch_id,
        ouen_batch_id=ouen_batch_id,
    ).subquery('ouen_keisan')

    alloc_q = db.session.query(AllocationData)
    if allocation_batch_id is not None:
        alloc_q = alloc_q.filter(AllocationData.batch_id == allocation_batch_id)
    alloc_sq = alloc_q.subquery('alloc')

    # 課単位の按分人員数合計（PARTITION BY 集約課コード の代替）
    ratio_total_sq = (
        db.session.query(
            alloc_sq.c.district_code,
            alloc_sq.c.section_code,
            func.sum(alloc_sq.c.allocation_ratio).label('total_ratio'),
        )
        .group_by(alloc_sq.c.district_code, alloc_sq.c.section_code)
        .subquery('ratio_total')
    )

    # 按分比率（人員比）の計算
    ratio_sq = (
        db.session.query(
            alloc_sq.c.district_code.label('district'),
            alloc_sq.c.section_code.label('section'),
            alloc_sq.c.allocation_ratio,
            (
                cast(alloc_sq.c.allocation_ratio, Float)
                / ratio_total_sq.c.total_ratio
            ).label('ninzuu_hi'),
        )
        .select_from(alloc_sq)
        .join(
            ratio_total_sq,
            (ratio_total_sq.c.district_code == alloc_sq.c.district_code)
            & (ratio_total_sq.c.section_code == alloc_sq.c.section_code),
        )
        .subquery('ratio')
    )

    q = (
        db.session.query(
            ratio_sq.c.district.label('chiku'),
            ratio_sq.c.section.label('ka_code'),
            SectionMaster.cost_center_code.label('cost_center'),
            ratio_sq.c.allocation_ratio,
            ratio_sq.c.ninzuu_hi,
            func.round(
                cast(ouen_keisan_sq.c.ouen_go_jinkenhi, Float)
                * ratio_sq.c.ninzuu_hi,
                0,
            ).label('koutei_haibun'),
        )
        .select_from(ratio_sq)
        .outerjoin(
            ouen_keisan_sq,
            (ouen_keisan_sq.c.chiku == ratio_sq.c.district)
            & (ouen_keisan_sq.c.ka_code == ratio_sq.c.section),
        )
        .outerjoin(
            SectionMaster,
            SectionMaster.section_code == ratio_sq.c.section,
        )
    )
    return q
