"""ORM-based file service.

Comparison pattern against file_service.py (db / raw-SQL pattern).

db パターン          → db_manager.*() → pd.DataFrame → FileRecord (dataclass)
ORM パターン (here)  → db.session.* / db.paginate() → UploadedFile (ORM model)
"""

import os
import uuid
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
from flask import current_app
from sqlalchemy import select, or_
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import UploadedFile

ALLOWED_EXTENSIONS: set[str] = {
    ".xlsx", ".xls", ".csv",
    ".pdf", ".png", ".jpg", ".jpeg", ".docx",
}

EXCEL_EXTENSIONS: set[str] = {".xlsx", ".xls"}

_SPREADSHEET_EXTENSIONS: set[str] = {".xlsx", ".xls", ".csv"}

_SORT_COLUMNS: frozenset[str] = frozenset(
    {"original_filename", "file_size", "mime_type", "status", "created_at"}
)

_SORT_ATTR_MAP: dict[str, object] = {
    "original_filename": UploadedFile.original_filename,
    "file_size":         UploadedFile.file_size,
    "mime_type":         UploadedFile.mime_type,
    "status":            UploadedFile.status,
    "created_at":        UploadedFile.created_at,
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# save_file
# ---------------------------------------------------------------------------

def save_file(file: FileStorage, username: str | None = None) -> UploadedFile:
    """Save an uploaded file to disk and create an ORM record.

    db パターンとの対比
    -------------------
    db  : db_manager.insert_df("uploaded_files", row_df)
          → fetch by stored_filename → FileRecord.from_row(...)
    ORM : UploadedFile(...) → db.session.add(record) → db.session.commit()
          → db.session.refresh(record)   # auto-generated id を取得
    """
    original_name = secure_filename(file.filename or "unnamed") or "unnamed"
    ext = os.path.splitext(original_name)[1].lower()

    stored_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir: str = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, stored_name)
    file.save(full_path)

    now = _now()
    record = UploadedFile(
        original_filename=original_name,
        stored_filename=stored_name,
        file_path=full_path,
        file_size=os.path.getsize(full_path),
        mime_type=file.mimetype or "",
        status="uploaded",
        row_count=None,
        sheet_names=None,
        error_message=None,
        created_by=username,
        updated_by=username,
        created_at=now,
        updated_at=now,
    )
    db.session.add(record)
    db.session.commit()
    db.session.refresh(record)  # id を確定させる

    if ext in _SPREADSHEET_EXTENSIONS:
        _process_spreadsheet(record, full_path, ext)
        record.updated_by = username
        record.updated_at = _now()
        db.session.commit()

    return record


# ---------------------------------------------------------------------------
# _process_spreadsheet
# ---------------------------------------------------------------------------

def _process_spreadsheet(record: UploadedFile, path: str, ext: str) -> None:
    """Read a spreadsheet with pandas and populate metadata on *record*.

    db パターンとの対比
    -------------------
    db  : FileRecord (dataclass) を変更 → 呼び出し元が db_manager.update() で保存
    ORM : UploadedFile (ORM model) を直接変更 → 呼び出し元が db.session.commit() で保存
          (SQLAlchemy の Unit of Work が変更を自動追跡する)
    """
    try:
        if ext == ".csv":
            df = pd.read_csv(path)
            record.row_count = len(df)
        else:
            xf = pd.ExcelFile(path)
            record.sheet_names = ",".join(xf.sheet_names)
            df = xf.parse(xf.sheet_names[0])
            record.row_count = len(df)
        record.status = "processed"
    except Exception as exc:  # noqa: BLE001
        record.status = "error"
        record.error_message = str(exc)[:1024]


# ---------------------------------------------------------------------------
# get_file_list
# ---------------------------------------------------------------------------

def get_file_list(
    page: int = 1,
    per_page: int = 20,
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
):
    """Return a paginated, filtered, and sorted list of UploadedFile records.

    db パターンとの対比
    -------------------
    db  : db_manager.fetch_page(sql, page, per_page, order_by=...) → (DataFrame, total)
          → SimplePagination[FileRecord]
    ORM : db.paginate(select(UploadedFile).where(...).order_by(...), page=, per_page=)
          → flask_sqlalchemy.pagination.QueryPagination
          (.items / .page / .per_page / .total / .pages / .has_prev / .has_next は同一 API)
    """
    safe_attr = _SORT_ATTR_MAP.get(sort_key, UploadedFile.created_at)
    order_col = safe_attr.asc() if sort_dir.lower() == "asc" else safe_attr.desc()

    stmt = select(UploadedFile)
    if q:
        stmt = stmt.where(UploadedFile.original_filename.like(f"%{q}%"))
    stmt = stmt.order_by(order_col)

    return db.paginate(stmt, page=page, per_page=per_page, count=True)


# ---------------------------------------------------------------------------
# get_file_by_id
# ---------------------------------------------------------------------------

def get_file_by_id(file_id: int) -> UploadedFile | None:
    """Fetch a single file record by primary key.

    db パターンとの対比
    -------------------
    db  : db_manager.fetch("SELECT * FROM uploaded_files WHERE id = :id", ...)
          → FileRecord.from_row(df.iloc[0])
    ORM : db.session.get(UploadedFile, file_id)
          (主キー検索は session.get() が最もシンプル)
    """
    return db.session.get(UploadedFile, file_id)


# ---------------------------------------------------------------------------
# delete_file
# ---------------------------------------------------------------------------

def delete_file(record: UploadedFile) -> None:
    """Remove the file from disk and delete the ORM record.

    db パターンとの対比
    -------------------
    db  : os.remove() → db_manager.delete("uploaded_files", "id = :id", ...)
    ORM : os.remove() → db.session.delete(record) → db.session.commit()
    """
    if os.path.exists(record.file_path):
        os.remove(record.file_path)
    db.session.delete(record)
    db.session.commit()


# ---------------------------------------------------------------------------
# export_to_excel
# ---------------------------------------------------------------------------

def export_to_excel(
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
) -> BytesIO:
    """Build an in-memory Excel workbook of the current file list.

    db パターンとの対比
    -------------------
    db  : db_manager.fetch(sql, params) → pd.DataFrame (直接 pandas に渡す)
    ORM : db.session.execute(select(...)) → ORM オブジェクトのリスト
          → pd.DataFrame([{...} for f in files]) で列を明示的に構築
    """
    safe_attr = _SORT_ATTR_MAP.get(sort_key, UploadedFile.created_at)
    order_col = safe_attr.asc() if sort_dir.lower() == "asc" else safe_attr.desc()

    stmt = select(UploadedFile)
    if q:
        stmt = stmt.where(UploadedFile.original_filename.like(f"%{q}%"))
    stmt = stmt.order_by(order_col)

    files = db.session.execute(stmt).scalars().all()

    export_df = pd.DataFrame([
        {
            "ファイル名":           f.original_filename,
            "サイズ (bytes)":       f.file_size,
            "MIMEタイプ":           f.mime_type or "",
            "ステータス":           f.status,
            "行数":                 f.row_count if f.row_count is not None else "",
            "アップロード日時":     (
                f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else ""
            ),
            "アップロードユーザー": f.created_by or "",
        }
        for f in files
    ])

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="ファイル一覧")
    buffer.seek(0)
    return buffer
