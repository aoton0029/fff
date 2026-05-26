from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .forms import ExcelImportForm
from . import service as svc

excel_imports_bp = Blueprint("excel_imports", __name__)


@excel_imports_bp.route("/")
@login_required
def index():
    """最初のドメインページへリダイレクト"""
    cfg = svc.get_domain_config()
    if not cfg:
        abort(404)
    first_domain = next(iter(cfg))
    return redirect(url_for("excel_imports.domain_page", domain=first_domain))


@excel_imports_bp.route("/<domain>/")
@login_required
def domain_page(domain: str):
    cfg = svc.get_domain_config()
    if domain not in cfg:
        abort(404)
    form = ExcelImportForm()
    domain_cfg = cfg[domain]
    return render_template(
        "excel_imports/index.html",
        form=form,
        domain=domain,
        domain_cfg=domain_cfg,
    )


@excel_imports_bp.route("/<domain>/upload", methods=["POST"])
@login_required
def upload(domain: str):
    cfg = svc.get_domain_config()
    if domain not in cfg:
        abort(404)

    form = ExcelImportForm()
    if not form.validate_on_submit():
        flash("入力内容に誤りがあります。", "danger")
        return redirect(url_for("excel_imports.domain_page", domain=domain))

    files = request.files.getlist("files")
    success_count, error_messages = svc.upload_files(files, domain, current_user.username)

    if success_count:
        flash(f"{success_count} 件のExcelを取り込みました。", "success")
    for msg in error_messages:
        flash(msg, "danger")

    return redirect(url_for("excel_imports.domain_page", domain=domain))
