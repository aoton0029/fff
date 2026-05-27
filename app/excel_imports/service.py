"""excel_imports/service.py — Excel取込ドメインのビジネスロジック"""

from __future__ import annotations

import io
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pandas as pd
import yaml

from sqlalchemy import select

from ..extensions import db
from ..models.excel_import import ExcelImport
from ..models.inventory_data import InventoryData
from ..models.sales_data import SalesData

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

# ───────────────────────────────────────────
# ドメイン設定
# ───────────────────────────────────────────

_ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".xlsx", ".xls"})

_DOMAIN_CONFIG: dict[str, Any] | None = None

# ドメイン → DB モデルクラスのマッピング
_DOMAIN_MODEL_MAP: dict[str, type] = {
    "sales": SalesData,
    "inventory": InventoryData,
}


def load_domain_config(app=None) -> dict[str, Any]:
    """instance/excel_domains.yml を読み込んで返す（アプリ起動後に一度だけ呼ぶ）"""
    global _DOMAIN_CONFIG
    if _DOMAIN_CONFIG is not None:
        return _DOMAIN_CONFIG

    if app is not None:
        config_path = os.path.join(app.instance_path, "excel_domains.yml")
    else:
        from flask import current_app
        config_path = os.path.join(current_app.instance_path, "excel_domains.yml")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    _DOMAIN_CONFIG = data.get("domains", {})
    return _DOMAIN_CONFIG


def get_domain_config() -> dict[str, Any]:
    """キャッシュ済みドメイン設定を返す"""
    if _DOMAIN_CONFIG is None:
        return load_domain_config()
    return _DOMAIN_CONFIG


def get_domain_choices() -> list[tuple[str, str]]:
    """SelectField 用 (value, label) リスト"""
    cfg = get_domain_config()
    return [(key, val["display_name"]) for key, val in cfg.items()]


# ───────────────────────────────────────────
# 複数ファイル取込（ビューから呼び出す入口）
# ───────────────────────────────────────────

def upload_files(
    files: list["FileStorage"],
    domain: str,
    username: str,
) -> tuple[int, list[str]]:
    """複数 Excel ファイルを取り込む。戻り値: (成功件数, エラーメッセージリスト)"""
    if not files or all(f.filename == "" for f in files):
        return 0, ["ファイルを選択してください。"]

    success_count = 0
    error_messages: list[str] = []

    for f in files:
        if not f.filename:
            continue
        ext = ("." + f.filename.rsplit(".", 1)[-1].lower()) if "." in f.filename else ""
        if ext not in _ALLOWED_EXTENSIONS:
            error_messages.append(
                f"「{f.filename}」は対応していない形式です（xlsx / xls のみ）"
            )
            continue
        try:
            process_excel_import(f, domain, username)
            success_count += 1
        except Exception as exc:
            error_messages.append(f"「{f.filename}」の取込に失敗しました: {exc}")

    return success_count, error_messages


# ───────────────────────────────────────────
# Excel 取込処理
# ───────────────────────────────────────────

def process_excel_import(
    file_storage: "FileStorage",
    domain: str,
    username: str,
) -> ExcelImport:
    cfg = get_domain_config()
    if domain not in cfg:
        raise ValueError(f"不明なドメインです: {domain}")

    domain_cfg = cfg[domain]
    import_record = ExcelImport(
        original_filename=file_storage.filename or "unknown.xlsx",
        domain=domain,
        status="imported",
        created_by=username,
        updated_by=username,
    )
    db.session.add(import_record)
    db.session.flush()

    try:
        file_bytes = io.BytesIO(file_storage.read())
        rows = _read_excel(file_bytes, domain_cfg)
        _save_rows(import_record.id, domain, rows, username)
        import_record.row_count = len(rows)
        import_record.status = "imported"
    except Exception as exc:
        import_record.status = "error"
        import_record.error_message = str(exc)[:1024]

    db.session.commit()
    return import_record


def _read_excel(
    file_bytes: io.BytesIO,
    domain_cfg: dict[str, Any],
) -> list[dict[str, str | None]]:
    header_row: int = domain_cfg.get("header_row", 1)
    usecols: str | None = domain_cfg.get("usecols") or None
    sheet_name: str = domain_cfg["sheet_name"]

    df = pd.read_excel(
        file_bytes,
        sheet_name=sheet_name,
        header=header_row - 1,
        usecols=usecols,
    )

    df = df.dropna(how="all")

    col_defs: list[dict] = domain_cfg.get("columns", [])
    rename_map: dict[str, str] = {}
    for col in col_defs:
        excel_col = col.get("excel_col") or col.get("label")
        rename_map[excel_col] = col["name"]

    df = df.rename(columns=rename_map)

    db_cols = [c["name"] for c in col_defs]
    existing_cols = [c for c in db_cols if c in df.columns]
    df = df[existing_cols]

    records = []
    for _, row in df.iterrows():
        record: dict[str, str | None] = {}
        for col in db_cols:
            val = row.get(col)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                record[col] = None
            else:
                record[col] = str(val)
        records.append(record)

    return records


def _save_rows(
    import_id: int,
    domain: str,
    rows: list[dict[str, str | None]],
    username: str,
) -> None:
    model_cls = _DOMAIN_MODEL_MAP.get(domain)
    if model_cls is None:
        raise ValueError(f"ドメイン '{domain}' に対応するモデルが見つかりません")

    objs = []
    for row_data in rows:
        obj = model_cls(import_id=import_id, created_by=username, updated_by=username)
        for key, val in row_data.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        objs.append(obj)

    db.session.bulk_save_objects(objs)


# ───────────────────────────────────────────
# 取込一覧取得
# ───────────────────────────────────────────

def get_import_list(
    page: int = 1,
    per_page: int = 20,
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
    domain: str | None = None,
):
    stmt = select(ExcelImport)

    if domain:
        stmt = stmt.where(ExcelImport.domain == domain)

    if q:
        stmt = stmt.where(ExcelImport.original_filename.ilike(f"%{q}%"))

    sortable = {
        "original_filename": ExcelImport.original_filename,
        "domain": ExcelImport.domain,
        "row_count": ExcelImport.row_count,
        "status": ExcelImport.status,
        "created_at": ExcelImport.created_at,
    }
    col = sortable.get(sort_key, ExcelImport.created_at)
    stmt = stmt.order_by(col.asc() if sort_dir == "asc" else col.desc())

    return db.paginate(stmt, page=page, per_page=per_page, error_out=False)


def get_import_by_id(import_id: int) -> ExcelImport | None:
    return db.session.get(ExcelImport, import_id)


# ───────────────────────────────────────────
# 承認（角印）
# ───────────────────────────────────────────

def approve_import(record: ExcelImport, username: str) -> None:
    """承認確定。一度確定すると取り消し不可。"""
    if record.status == "approved":
        return
    record.status = "approved"
    record.approved_at = datetime.now()
    record.approved_by = username
    record.updated_by = username
    db.session.commit()


# ───────────────────────────────────────────
# 削除
# ───────────────────────────────────────────

def delete_import(record: ExcelImport) -> None:
    """ExcelImport とドメインデータ行（CASCADE）を削除する"""
    model_cls = _DOMAIN_MODEL_MAP.get(record.domain)
    if model_cls is not None:
        db.session.execute(
            db.delete(model_cls).where(model_cls.import_id == record.id)
        )
    db.session.delete(record)
    db.session.commit()


# ───────────────────────────────────────────
# データ確認（モーダル用）
# ───────────────────────────────────────────

def get_import_rows(import_id: int, domain: str) -> list[Any]:
    model_cls = _DOMAIN_MODEL_MAP.get(domain)
    if model_cls is None:
        return []
    return db.session.execute(
        select(model_cls).where(model_cls.import_id == import_id)
    ).scalars().all()
