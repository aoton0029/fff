<<<<<<< HEAD
# Deprecated: use app.files.api (registered as files_api blueprint)
from ..files.api import files_api_bp  # noqa: F401
from ..services.file_service import delete_file as svc_delete_file
=======
import os

import pandas as pd
from flask import jsonify, request, render_template, send_file
from flask_login import current_user, login_required

from . import api_bp
from ..services.file_service import (
    get_file_list, export_to_excel, get_file_by_id,
    delete_file as svc_delete_file,
    save_file, EXCEL_EXTENSIONS,
)
from werkzeug.utils import secure_filename
>>>>>>> 4338afad389814a878391d7019d553facd2a4f71

_COLUMNS = [
    {"key": "original_filename", "label": "ファイル名",       "sortable": True},
    {"key": "file_size",         "label": "サイズ",           "sortable": True},
    {"key": "mime_type",         "label": "種類",             "sortable": True},
    {"key": "status",            "label": "ステータス",       "sortable": True},
    {"key": "created_at",        "label": "アップロード日時", "sortable": True},
    {"key": "actions",           "label": "",                 "sortable": False},
]


@api_bp.route("/files/table")
@login_required
def files_table():
    page     = request.args.get("page",     1,            type=int)
    per_page = request.args.get("per_page", 20,           type=int)
    q        = request.args.get("q",        "",           type=str)
    sort_key = request.args.get("sort_key", "created_at", type=str)
    sort_dir = request.args.get("sort_dir", "desc",       type=str)

    pagination = get_file_list(
        page=page, per_page=per_page, q=q, sort_key=sort_key, sort_dir=sort_dir
    )
    return render_template(
        "files/_table_fragment.html",
        columns=_COLUMNS,
        files=pagination.items,
        pagination={
            "page": pagination.page,
            "per_page": per_page,
            "total": pagination.total,
        },
        sort_key=sort_key,
        sort_dir=sort_dir,
        filter_value=q,
    )


@api_bp.route("/files/<int:file_id>/detail")
@login_required
def file_detail_fragment(file_id: int):
    record = get_file_by_id(file_id)
    if record is None:
        return '<p class="text-danger mb-0">ファイルが見つかりません。</p>', 404
    return render_template("files/_detail_fragment.html", file=record)


@api_bp.route("/files/<int:file_id>/delete", methods=["POST"])
@login_required
def file_delete_api(file_id: int):
    record = get_file_by_id(file_id)
    if record:
        svc_delete_file(record)

    page     = request.args.get("page",     1,            type=int)
    per_page = request.args.get("per_page", 20,           type=int)
    q        = request.args.get("q",        "",           type=str)
    sort_key = request.args.get("sort_key", "created_at", type=str)
    sort_dir = request.args.get("sort_dir", "desc",       type=str)

    pagination = get_file_list(
        page=page, per_page=per_page, q=q, sort_key=sort_key, sort_dir=sort_dir
    )
    return render_template(
        "files/_table_fragment.html",
        columns=_COLUMNS,
        files=pagination.items,
        pagination={
            "page": pagination.page,
            "per_page": per_page,
            "total": pagination.total,
        },
        sort_key=sort_key,
        sort_dir=sort_dir,
        filter_value=q,
    )


@api_bp.route("/files/export")
@login_required
def files_export():
    q        = request.args.get("q",        "",           type=str)
    sort_key = request.args.get("sort_key", "created_at", type=str)
    sort_dir = request.args.get("sort_dir", "desc",       type=str)

    buffer = export_to_excel(q=q, sort_key=sort_key, sort_dir=sort_dir)
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="files_export.xlsx",
    )


@api_bp.route("/files/upload-one", methods=["POST"])
@login_required
def upload_one():
    """Accept a single Excel file and return JSON with the processing result."""
    f = request.files.get("file")
    if f is None or not f.filename:
        return jsonify({"error": "ファイルが選択されていません"}), 400

    original_name = secure_filename(f.filename)
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in EXCEL_EXTENSIONS:
        return jsonify({"error": f"Excelファイル（.xlsx / .xls）のみ対応しています: {f.filename}"}), 400

    try:
        record = save_file(f, username=current_user.username)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "id":            record.id,
        "filename":      record.original_filename,
        "file_size":     record.file_size,
        "status":        record.status,
        "row_count":     record.row_count,
        "sheet_names":   record.sheet_names,
        "error_message": record.error_message,
    })


@api_bp.route("/files/<int:file_id>/preview")
@login_required
def file_preview(file_id: int):
    """Return a JSON preview (up to 500 rows) of the first sheet of an Excel file."""
    record = get_file_by_id(file_id)
    if record is None:
        return jsonify({"error": "ファイルが見つかりません"}), 404

    ext = os.path.splitext(record.stored_filename)[1].lower()
    if ext not in EXCEL_EXTENSIONS:
        return jsonify({"error": "Excelファイルではありません"}), 400

    if not os.path.exists(record.file_path):
        return jsonify({"error": "ファイルが存在しません"}), 404

    MAX_ROWS = 500
    try:
        xf = pd.ExcelFile(record.file_path)
        sheet_name = xf.sheet_names[0]
        df = xf.parse(sheet_name, nrows=MAX_ROWS)
        columns = df.columns.astype(str).tolist()
        rows: list = []
        for _, row_data in df.iterrows():
            clean: list = []
            for val in row_data:
                try:
                    if pd.isna(val):
                        clean.append(None)
                        continue
                except (TypeError, ValueError):
                    pass
                if hasattr(val, "item"):  # numpy scalar
                    clean.append(val.item())
                elif isinstance(val, pd.Timestamp):
                    clean.append(val.isoformat())
                else:
                    clean.append(val)
            rows.append(clean)
        return jsonify({
            "columns":    columns,
            "rows":       rows,
            "sheet_name": sheet_name,
            "total_rows": record.row_count,
            "filename":   record.original_filename,
        })
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@api_bp.route("/files/<int:file_id>/delete-json", methods=["POST"])
@login_required
def file_delete_json(file_id: int):
    """Delete a file and return JSON (used by the excel-extract page)."""
    record = get_file_by_id(file_id)
    if record is None:
        return jsonify({"error": "ファイルが見つかりません"}), 404
    svc_delete_file(record)
    return jsonify({"success": True})
