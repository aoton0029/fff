"""ORM-based file views.

Comparison pattern against views/files.py (db / raw-SQL pattern).

db パターン  → /files/*        (files_bp     in views/files.py)
             uses file_service  → FileRecord (dataclass)

ORM パターン → /orm/files/*    (files_orm_bp in views/files_orm.py)
             uses file_service_orm → UploadedFile (ORM model)

テンプレートは共通で使い回す。
UploadedFile と FileRecord は属性名が同一なので変更不要。
"""

import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..forms.file_form import FileUploadForm
from ..services import file_service_orm
from ..services.file_service_orm import ALLOWED_EXTENSIONS

files_orm_bp = Blueprint("files_orm", __name__, url_prefix="/orm/files")

_COLUMNS = [
    {"key": "original_filename", "label": "ファイル名",       "sortable": True},
    {"key": "file_size",         "label": "サイズ",           "sortable": True},
    {"key": "mime_type",         "label": "種類",             "sortable": True},
    {"key": "status",            "label": "ステータス",       "sortable": True},
    {"key": "created_at",        "label": "アップロード日時", "sortable": True},
    {"key": "actions",           "label": "",                 "sortable": False},
]


@files_orm_bp.route("/")
@login_required
def index():
    return render_template("orm/files/index.html", columns=_COLUMNS)


@files_orm_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """db パターンとの対比
    -------------------
    db  : file_service.save_file(f, username)
          → db_manager.insert_df() → FileRecord
    ORM : file_service_orm.save_file(f, username)
          → db.session.add(record) → db.session.commit() → UploadedFile
    """
    form = FileUploadForm()
    if form.validate_on_submit():
        uploaded = request.files.getlist("files")
        if not uploaded or all(f.filename == "" for f in uploaded):
            flash("ファイルを選択してください。", "warning")
            return redirect(request.url)

        saved, errors = [], []
        for f in uploaded:
            if not f.filename:
                continue
            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                errors.append(f"{f.filename}: 対応していないファイル形式です")
                continue
            try:
                file_service_orm.save_file(f, username=current_user.username)
                saved.append(f.filename)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{f.filename}: {exc}")

        for msg in errors:
            flash(msg, "danger")
        if saved:
            flash(f"{len(saved)} 件のファイルをアップロードしました。", "success")
        return redirect(url_for("files_orm.index"))

    return render_template("orm/files/upload.html", form=form)


@files_orm_bp.route("/excel-extract")
@login_required
def excel_extract():
    return render_template("orm/files/excel_extract.html")


@files_orm_bp.route("/<int:file_id>")
@login_required
def detail(file_id: int):
    """db パターンとの対比
    -------------------
    db  : file_service.get_file_by_id(id) → FileRecord | None
    ORM : file_service_orm.get_file_by_id(id) → db.session.get(UploadedFile, id)
    """
    record = file_service_orm.get_file_by_id(file_id)
    if record is None:
        flash("ファイルが見つかりません。", "danger")
        return redirect(url_for("files_orm.index"))
    return render_template("orm/files/detail.html", file=record)


@files_orm_bp.route("/<int:file_id>/delete", methods=["POST"])
@login_required
def delete(file_id: int):
    """db パターンとの対比
    -------------------
    db  : db_manager.delete("uploaded_files", "id = :id", {"id": record.id})
    ORM : db.session.delete(record) → db.session.commit()
    """
    record = file_service_orm.get_file_by_id(file_id)
    if record is None:
        flash("ファイルが見つかりません。", "danger")
    else:
        filename = record.original_filename
        file_service_orm.delete_file(record)
        flash(f"「{filename}」を削除しました。", "success")
    return redirect(url_for("files_orm.index"))
