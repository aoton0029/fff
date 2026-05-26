import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .forms import FileUploadForm
from .service import ALLOWED_EXTENSIONS, delete_file, get_file_by_id, save_file

files_bp = Blueprint("files", __name__)

_COLUMNS = [
    {"key": "original_filename", "label": "ファイル名",       "sortable": True},
    {"key": "file_size",         "label": "サイズ",           "sortable": True},
    {"key": "mime_type",         "label": "種類",             "sortable": True},
    {"key": "status",            "label": "ステータス",       "sortable": True},
    {"key": "created_at",        "label": "アップロード日時", "sortable": True},
    {"key": "actions",           "label": "",                 "sortable": False},
]


@files_bp.route("/")
@login_required
def index():
    return render_template("files/index.html", columns=_COLUMNS)


@files_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
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
                save_file(f, username=current_user.username)
                saved.append(f.filename)
            except Exception as exc:
                errors.append(f"{f.filename}: {exc}")

        for msg in errors:
            flash(msg, "danger")
        if saved:
            flash(f"{len(saved)} 件のファイルをアップロードしました。", "success")
        return redirect(url_for("files.index"))

    return render_template("files/upload.html", form=form)


@files_bp.route("/<int:file_id>")
@login_required
def detail(file_id: int):
    record = get_file_by_id(file_id)
    if record is None:
        flash("ファイルが見つかりません。", "danger")
        return redirect(url_for("files.index"))
    return render_template("files/detail.html", file=record)


@files_bp.route("/<int:file_id>/delete", methods=["POST"])
@login_required
def delete(file_id: int):
    record = get_file_by_id(file_id)
    if record is None:
        flash("ファイルが見つかりません。", "danger")
    else:
        filename = record.original_filename
        delete_file(record)
        flash(f"「{filename}」を削除しました。", "success")
    return redirect(url_for("files.index"))
