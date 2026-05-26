# Deprecated: use app.excel_imports.service
from ..excel_imports.service import (  # noqa: F401
    load_domain_config,
    get_domain_config,
    get_domain_choices,
    upload_files,
    process_excel_import,
    get_import_list,
    get_import_by_id,
    approve_import,
    delete_import,
    get_import_rows,
)


def load_domain_config(app=None) -> dict[str, Any]:
    """instance/excel_domains.yml を読み込んで返す（アプリ起動後に一度だけ呼ぶ）"""
    global _DOMAIN_CONFIG
    if _DOMAIN_CONFIG is not None:
        return _DOMAIN_CONFIG

    # Flask app context がある場合は instance_path を優先
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
# Excel 取込処理
# ───────────────────────────────────────────

def process_excel_import(
    file_storage: "FileStorage",
    domain: str,
    username: str,
) -> ExcelImport:
    """
    FileStorage を受け取り、ドメイン設定に従ってシートを読み込み、
    ExcelImport + ドメイン専用テーブルに保存する。
    ファイル自体はディスクに保存しない。
    """
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
    db.session.flush()  # id を確定させる

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
    """
    pandas で Excel を読み込み、列名を DB カラム名にマッピングして返す。
    ・header_row: 1始まり整数（pandas の header パラメータは 0始まりに変換）
    ・usecols   : "B:F" 形式、または null（全列）
    """
    header_row: int = domain_cfg.get("header_row", 1)
    usecols: str | None = domain_cfg.get("usecols") or None
    sheet_name: str = domain_cfg["sheet_name"]

    df = pd.read_excel(
        file_bytes,
        sheet_name=sheet_name,
        header=header_row - 1,          # pandas は 0始まり
        usecols=usecols,
    )

    # 空行を除去
    df = df.dropna(how="all")

    # Excel列名 → DB列名へリネーム
    col_defs: list[dict] = domain_cfg.get("columns", [])
    rename_map: dict[str, str] = {}
    for col in col_defs:
        excel_col = col.get("excel_col") or col.get("label")
        rename_map[excel_col] = col["name"]

    df = df.rename(columns=rename_map)

    # DB カラム名のみ抽出（YAML で定義された列だけ）
    db_cols = [c["name"] for c in col_defs]
    existing_cols = [c for c in db_cols if c in df.columns]
    df = df[existing_cols]

    # 全値を str に変換（NaN は None に）
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
    query = ExcelImport.query

    if domain:
        query = query.filter(ExcelImport.domain == domain)

    if q:
        query = query.filter(ExcelImport.original_filename.ilike(f"%{q}%"))

    sortable = {
        "original_filename": ExcelImport.original_filename,
        "domain": ExcelImport.domain,
        "row_count": ExcelImport.row_count,
        "status": ExcelImport.status,
        "created_at": ExcelImport.created_at,
    }
    col = sortable.get(sort_key, ExcelImport.created_at)
    query = query.order_by(col.asc() if sort_dir == "asc" else col.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


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
        model_cls.query.filter_by(import_id=record.id).delete()
    db.session.delete(record)
    db.session.commit()


# ───────────────────────────────────────────
# データ確認（モーダル用）
# ───────────────────────────────────────────

def get_import_rows(import_id: int, domain: str) -> list[Any]:
    model_cls = _DOMAIN_MODEL_MAP.get(domain)
    if model_cls is None:
        return []
    return model_cls.query.filter_by(import_id=import_id).all()
