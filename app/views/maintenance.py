from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..models.section import SectionMaster
from ..models.department import DepartmentMaster

PER_PAGE = 30


# ---- Section Master ----

@main_bp.route('/maintenance/section')
@login_required
def section_list():
    page = request.args.get('page', 1, type=int)
    query = SectionMaster.query.order_by(SectionMaster.section_code)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('maintenance_section.html', sections=pagination.items, pagination=pagination)


# ---- Department Master ----

@main_bp.route('/maintenance/department')
@login_required
def department_list():
    page = request.args.get('page', 1, type=int)
    query = DepartmentMaster.query.order_by(DepartmentMaster.department_code)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('maintenance_department.html', departments=pagination.items, pagination=pagination)


# ---- Data Output ----

@main_bp.route('/maintenance/data-output')
@login_required
def data_output():
    return render_template('maintenance_data_output.html')
