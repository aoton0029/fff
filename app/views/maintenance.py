from flask import render_template, request, session
from flask_login import login_required
from sqlalchemy import select

from . import main_bp
from ..extensions import db
from ..models.mst_section import SectionMaster
from ..models.mst_department import DepartmentMaster

PER_PAGE = 30


# ---- Section Master ----

@main_bp.route('/maintenance/section')
@login_required
def section_list():
    page = request.args.get('page', 1, type=int)
    query = select(SectionMaster).order_by(SectionMaster.section_code)
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    section_import_uuid = session.get('section_import_uuid', '')
    return render_template(
        'maintenance_section.html',
        sections=pagination.items,
        pagination=pagination,
        section_import_uuid=section_import_uuid,
    )


# ---- Department Master ----

@main_bp.route('/maintenance/department')
@login_required
def department_list():
    page = request.args.get('page', 1, type=int)
    query = select(DepartmentMaster).order_by(DepartmentMaster.department_code)
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    department_import_uuid = session.get('department_import_uuid', '')
    return render_template(
        'maintenance_department.html',
        departments=pagination.items,
        pagination=pagination,
        department_import_uuid=department_import_uuid,
    )


# ---- Data Output ----

@main_bp.route('/maintenance/data-output')
@login_required
def data_output():
    return render_template('maintenance_data_output.html')
