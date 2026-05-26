# Deprecated: use app.excel_imports.views
from ..excel_imports.views import excel_imports_bp  # noqa: F401

__all__ = ["excel_imports_bp"]

_ALLOWED_EXT = {".xlsx", ".xls"}


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
    if not files or all(f.filename == "" for f in files):
        flash("ファイルを選択してください。", "warning")
        return redirect(url_for("excel_imports.domain_page", domain=domain))

    success_count = 0
    error_messages = []

    for f in files:
        if not f.filename:
            continue
        ext = "." + f.filename.rsplit(".", 1)[-1].lower()
        if ext not in _ALLOWED_EXT:
            error_messages.append(f"「{f.filename}」は対応していない形式です（xlsx / xls のみ）")
            continue

        try:
            svc.process_excel_import(f, domain, current_user.username)
            success_count += 1
        except Exception as exc:
            error_messages.append(f"「{f.filename}」の取込に失敗しました: {exc}")

    if success_count:
        flash(f"{success_count} 件のExcelを取り込みました。", "success")
    for msg in error_messages:
        flash(msg, "danger")

    return redirect(url_for("excel_imports.domain_page", domain=domain))
