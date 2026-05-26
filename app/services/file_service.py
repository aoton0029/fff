<<<<<<< HEAD
# Deprecated: use app.files.service
from ..files.service import (  # noqa: F401
    ALLOWED_EXTENSIONS,
    save_file,
    get_file_list,
    get_file_by_id,
    delete_file,
    export_to_excel,
)

__all__ = [
    "ALLOWED_EXTENSIONS",
    "save_file",
    "get_file_list",
    "get_file_by_id",
    "delete_file",
    "export_to_excel",
]
=======
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..db import db_manager
from ..db.records import FileRecord, SimplePagination

ALLOWED_EXTENSIONS: set[str] = {
    ".xlsx", ".xls", ".csv",
    ".pdf", ".png", ".jpg", ".jpeg", ".docx",
}
>>>>>>> 4338afad389814a878391d7019d553facd2a4f71

EXCEL_EXTENSIONS: set[str] = {".xlsx", ".xls"}

_SPREADSHEET_EXTENSIONS: set[str] = {".xlsx", ".xls", ".csv"}

_SORT_COLUMNS: frozenset[str] = frozenset(
    {"original_filename", "file_size", "mime_type", "status", "created_at"}
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def save_file(file: FileStorage, username: str | None = None) -> FileRecord:
    """Save an uploaded file to disk and create a database record."""
    original_name = secure_filename(file.filename or "unnamed") or "unnamed"
    ext = os.path.splitext(original_name)[1].lower()

    stored_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir: str = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, stored_name)
    file.save(full_path)

    now = _now()
    row_df = pd.DataFrame([{
        "original_filename": original_name,
        "stored_filename":   stored_name,
        "file_path":         full_path,
        "file_size":         os.path.getsize(full_path),
        "mime_type":         file.mimetype or "",
        "status":            "uploaded",
        "row_count":         None,
        "sheet_names":       None,
        "error_message":     None,
        "created_by":        username,
        "updated_by":        username,
        "created_at":        now,
        "updated_at":        now,
    }])
    db_manager.insert_df("uploaded_files", row_df)

    df = db_manager.fetch(
        "SELECT * FROM uploaded_files WHERE stored_filename = :sf",
        {"sf": stored_name},
    )
    record = FileRecord.from_row(df.iloc[0])

    if ext in _SPREADSHEET_EXTENSIONS:
        _process_spreadsheet(record, full_path, ext)
        db_manager.update(
            "uploaded_files",
            {
                "status":        record.status,
                "row_count":     record.row_count,
                "sheet_names":   record.sheet_names,
                "error_message": record.error_message,
                "updated_by":    username,
                "updated_at":    _now(),
            },
            "id = :_id",
            {"_id": record.id},
        )

    return record


def _process_spreadsheet(record: FileRecord, path: str, ext: str) -> None:
    """Read a spreadsheet with pandas and populate metadata on *record*."""
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


def get_file_list(
    page: int = 1,
    per_page: int = 20,
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
) -> SimplePagination[FileRecord]:
    """Return a paginated, filtered, and sorted list of file records."""
    safe_key = sort_key if sort_key in _SORT_COLUMNS else "created_at"
    safe_dir = "ASC" if sort_dir.lower() == "asc" else "DESC"
    order_by = f"{safe_key} {safe_dir}"

    if q:
        base_sql = (
            "SELECT * FROM uploaded_files"
            " WHERE original_filename LIKE :q"
        )
        params: dict = {"q": f"%{q}%"}
    else:
        base_sql = "SELECT * FROM uploaded_files"
        params = {}

    df, total = db_manager.fetch_page(
        base_sql, page, per_page, order_by=order_by, params=params
    )
    items = [FileRecord.from_row(row) for _, row in df.iterrows()]
    return SimplePagination(items=items, page=page, per_page=per_page, total=total)


def get_file_by_id(file_id: int) -> FileRecord | None:
    df = db_manager.fetch(
        "SELECT * FROM uploaded_files WHERE id = :id",
        {"id": file_id},
    )
    if df.empty:
        return None
    return FileRecord.from_row(df.iloc[0])


def delete_file(record: FileRecord) -> None:
    """Remove the file from disk and delete the database record."""
    if os.path.exists(record.file_path):
        os.remove(record.file_path)
    db_manager.delete("uploaded_files", "id = :id", {"id": record.id})


def export_to_excel(
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
) -> BytesIO:
    """Build an in-memory Excel workbook of the current file list."""
    safe_key = sort_key if sort_key in _SORT_COLUMNS else "created_at"
    safe_dir = "ASC" if sort_dir.lower() == "asc" else "DESC"

    if q:
        sql = (
            f"SELECT * FROM uploaded_files"
            f" WHERE original_filename LIKE :q"
            f" ORDER BY {safe_key} {safe_dir}"
        )
        params: dict = {"q": f"%{q}%"}
    else:
        sql = f"SELECT * FROM uploaded_files ORDER BY {safe_key} {safe_dir}"
        params = {}

    df = db_manager.fetch(sql, params)

    export_df = pd.DataFrame({
        "ファイル名":         df["original_filename"],
        "サイズ (bytes)":     df["file_size"],
        "MIMEタイプ":         df["mime_type"].fillna(""),
        "ステータス":         df["status"],
        "行数":               df["row_count"].fillna(""),
        "アップロード日時":   df["created_at"].apply(
            lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(x) else ""
        ),
        "アップロードユーザー": df["created_by"].fillna(""),
    })

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="ファイル一覧")
    buffer.seek(0)
    return buffer

