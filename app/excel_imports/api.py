from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from . import service as svc

excel_imports_api_bp = Blueprint("excel_imports_api", __name__)


def _render_table(domain: str, q: str = "", sort_key: str = "created_at", sort_dir: str = "desc"):
    """承認・削除後のテーブル再描画ヘルパー"""
    pagination = svc.get_import_list(q=q, sort_key=sort_key, sort_dir=sort_dir, domain=domain)
    domain_config = svc.get_domain_config()
    col_defs = domain_config.get(domain, {}).get("columns", [])
    return render_template(
        "excel_imports/_table_fragment.html",
        imports=pagination.items,
        pagination=pagination,
        filter_value=q,
        sort_key=sort_key,
        sort_dir=sort_dir,
        domain=domain,
        col_defs=col_defs,
    )


@excel_imports_api_bp.route("/<domain>/table")
@login_required
def excel_imports_table(domain: str):
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    q        = request.args.get("q", "")
    sort_key = request.args.get("sort_key", "created_at")
    sort_dir = request.args.get("sort_dir", "desc")

    pagination = svc.get_import_list(page, per_page, q, sort_key, sort_dir, domain=domain)
    domain_config = svc.get_domain_config()
    col_defs = domain_config.get(domain, {}).get("columns", [])

    return render_template(
        "excel_imports/_table_fragment.html",
        imports=pagination.items,
        pagination=pagination,
        filter_value=q,
        sort_key=sort_key,
        sort_dir=sort_dir,
        domain=domain,
        col_defs=col_defs,
    )


@excel_imports_api_bp.route("/<int:import_id>/approve", methods=["POST"])
@login_required
def excel_import_approve(import_id: int):
    record = svc.get_import_by_id(import_id)
    if record is None:
        return ("not found", 404)
    svc.approve_import(record, current_user.username)
    return _render_table(record.domain)


@excel_imports_api_bp.route("/<int:import_id>/delete", methods=["POST"])
@login_required
def excel_import_delete(import_id: int):
    record = svc.get_import_by_id(import_id)
    domain = record.domain if record else ""
    if record is not None:
        svc.delete_import(record)
    return _render_table(domain)


@excel_imports_api_bp.route("/<int:import_id>/data")
@login_required
def excel_import_data(import_id: int):
    record = svc.get_import_by_id(import_id)
    if record is None:
        return ("<p class='text-danger'>データが見つかりません</p>", 404)

    rows = svc.get_import_rows(import_id, record.domain)
    domain_config = svc.get_domain_config()
    col_defs = domain_config.get(record.domain, {}).get("columns", [])

    return render_template(
        "excel_imports/_data_table_fragment.html",
        record=record,
        rows=rows,
        col_defs=col_defs,
    )
