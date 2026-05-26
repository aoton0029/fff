import os
import uuid
from io import BytesIO

import pandas as pd
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models.file import UploadedFile

ALLOWED_EXTENSIONS: set[str] = {
    ".xlsx", ".xls", ".csv",
    ".pdf", ".png", ".jpg", ".jpeg", ".docx",
}

_SPREADSHEET_EXTENSIONS: set[str] = {".xlsx", ".xls", ".csv"}


def save_file(file: FileStorage, username: str | None = None) -> UploadedFile:
    original_name = secure_filename(file.filename or "unnamed") or "unnamed"
    ext = os.path.splitext(original_name)[1].lower()

    stored_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir: str = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, stored_name)
    file.save(full_path)

    record = UploadedFile(
        original_filename=original_name,
        stored_filename=stored_name,
        file_path=full_path,
        file_size=os.path.getsize(full_path),
        mime_type=file.mimetype or "",
        status="uploaded",
        created_by=username,
        updated_by=username,
    )
    db.session.add(record)
    db.session.flush()

    if ext in _SPREADSHEET_EXTENSIONS:
        _process_spreadsheet(record, full_path, ext)

    db.session.commit()
    return record


def _process_spreadsheet(record: UploadedFile, path: str, ext: str) -> None:
    try:
        df = pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
        record.row_count = len(df)
        record.status = "processed"
    except Exception as exc:
        record.status = "error"
        record.error_message = str(exc)[:1024]


def get_file_list(
    page: int = 1,
    per_page: int = 20,
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
):
    _col_map = {
        "original_filename": UploadedFile.original_filename,
        "file_size": UploadedFile.file_size,
        "mime_type": UploadedFile.mime_type,
        "status": UploadedFile.status,
        "created_at": UploadedFile.created_at,
    }
    query = UploadedFile.query
    if q:
        query = query.filter(UploadedFile.original_filename.ilike(f"%{q}%"))
    col = _col_map.get(sort_key, UploadedFile.created_at)
    query = query.order_by(col.asc() if sort_dir == "asc" else col.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_file_by_id(file_id: int) -> UploadedFile | None:
    return db.session.get(UploadedFile, file_id)


def delete_file(record: UploadedFile) -> None:
    if os.path.exists(record.file_path):
        os.remove(record.file_path)
    db.session.delete(record)
    db.session.commit()


def export_to_excel(
    q: str = "",
    sort_key: str = "created_at",
    sort_dir: str = "desc",
) -> BytesIO:
    pagination = get_file_list(
        page=1, per_page=100_000, q=q, sort_key=sort_key, sort_dir=sort_dir
    )
    rows = [
        {
            "ファイル名": f.original_filename,
            "サイズ (bytes)": f.file_size,
            "MIMEタイプ": f.mime_type or "",
            "ステータス": f.status,
            "行数": f.row_count if f.row_count is not None else "",
            "アップロード日時": (
                f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else ""
            ),
            "アップロードユーザー": f.created_by or "",
        }
        for f in pagination.items
    ]
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(rows).to_excel(writer, index=False, sheet_name="ファイル一覧")
    buffer.seek(0)
    return buffer
