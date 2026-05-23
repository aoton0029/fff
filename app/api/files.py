from flask import request, render_template, send_file
from flask_login import login_required

from . import api_bp
from ..services.file_service import get_file_list, export_to_excel, get_file_by_id
from ..services.file_service import delete_file as svc_delete_file

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
