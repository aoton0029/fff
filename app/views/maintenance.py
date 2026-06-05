from flask import render_template, request, session
from flask_login import login_required
from sqlalchemy import select

from . import main_bp
from ..extensions import db
from ..models.mst_section import SectionMaster
from ..models.mst_department import DepartmentMaster
from ..models.mst_district import DistrictMaster
from ..models.mst_kbn import KbnMaster
from ..models.mst_cost_center import CostCenterMaster
from ..models.mst_account import AccountMaster

PER_PAGE = 30


# ---- Section Master ----

@main_bp.route('/maintenance/section')
@login_required
def section_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'section_code')
    order = request.args.get('order', 'asc')
    q = request.args.get('q', '').strip()
    col_map = {
        'section_code': SectionMaster.section_code,
        'section_name': SectionMaster.section_name,
        'district_code': SectionMaster.district_code,
        'cost_center_code': SectionMaster.cost_center_code,
    }
    col = col_map.get(sort, SectionMaster.section_code)
    query = select(SectionMaster).order_by(col.desc() if order == 'desc' else col.asc())
    if q:
        query = query.where(
            SectionMaster.section_code.ilike(f'%{q}%') |
            SectionMaster.section_name.ilike(f'%{q}%')
        )
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    section_import_uuid = session.get('section_import_uuid', '')
    districts = db.session.scalars(select(DistrictMaster).order_by(DistrictMaster.district_code)).all()
    cost_centers = db.session.scalars(select(CostCenterMaster).order_by(CostCenterMaster.cost_center_code)).all()
    template = 'partials/section_table.html' if request.headers.get('HX-Request') else 'maintenance_section.html'
    return render_template(
        template,
        sections=pagination.items,
        pagination=pagination,
        section_import_uuid=section_import_uuid,
        districts=districts,
        cost_centers=cost_centers,
        sort=sort,
        order=order,
        q=q,
    )


# ---- Department Master ----

@main_bp.route('/maintenance/department')
@login_required
def department_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'department_code')
    order = request.args.get('order', 'asc')
    col_map = {
        'department_code': DepartmentMaster.department_code,
        'department_name': DepartmentMaster.department_name,
        'district_code': DepartmentMaster.district_code,
        'section_code': DepartmentMaster.section_code,
        'account_code': DepartmentMaster.account_code,
        'cost_center_code': DepartmentMaster.cost_center_code,
    }
    col = col_map.get(sort, DepartmentMaster.department_code)
    query = select(DepartmentMaster).order_by(col.desc() if order == 'desc' else col.asc())
    q = request.args.get('q', '').strip()
    if q:
        query = query.where(
            DepartmentMaster.department_code.ilike(f'%{q}%') |
            DepartmentMaster.department_name.ilike(f'%{q}%')
        )
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    department_import_uuid = session.get('department_import_uuid', '')
    districts = db.session.scalars(select(DistrictMaster).order_by(DistrictMaster.district_code)).all()
    sections = db.session.scalars(select(SectionMaster).order_by(SectionMaster.section_code)).all()
    kbns = db.session.scalars(select(KbnMaster).order_by(KbnMaster.kbn_code)).all()
    accounts = db.session.scalars(select(AccountMaster).order_by(AccountMaster.account_code)).all()
    cost_centers = db.session.scalars(select(CostCenterMaster).order_by(CostCenterMaster.cost_center_code)).all()
    template = 'partials/department_table.html' if request.headers.get('HX-Request') else 'maintenance_department.html'
    return render_template(
        template,
        departments=pagination.items,
        pagination=pagination,
        department_import_uuid=department_import_uuid,
        districts=districts,
        sections=sections,
        kbns=kbns,
        accounts=accounts,
        cost_centers=cost_centers,
        sort=sort,
        order=order,
        q=q,
    )


# ---- Data Output ----

@main_bp.route('/maintenance/district')
@login_required
def district_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'district_code')
    order = request.args.get('order', 'asc')
    q = request.args.get('q', '').strip()
    col_map = {
        'district_code': DistrictMaster.district_code,
        'district_name': DistrictMaster.district_name,
    }
    col = col_map.get(sort, DistrictMaster.district_code)
    query = select(DistrictMaster).order_by(col.desc() if order == 'desc' else col.asc())
    if q:
        query = query.where(
            DistrictMaster.district_code.ilike(f'%{q}%') |
            DistrictMaster.district_name.ilike(f'%{q}%')
        )
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    district_import_uuid = session.get('district_import_uuid', '')
    template = 'partials/district_table.html' if request.headers.get('HX-Request') else 'maintenance_district.html'
    return render_template(
        template,
        districts=pagination.items,
        pagination=pagination,
        district_import_uuid=district_import_uuid,
        sort=sort,
        order=order,
        q=q,
    )


# ---- Kbn Master ----

@main_bp.route('/maintenance/kbn')
@login_required
def kbn_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'kbn_code')
    order = request.args.get('order', 'asc')
    q = request.args.get('q', '').strip()
    col_map = {
        'kbn_code': KbnMaster.kbn_code,
        'kbn_name': KbnMaster.kbn_name,
    }
    col = col_map.get(sort, KbnMaster.kbn_code)
    query = select(KbnMaster).order_by(col.desc() if order == 'desc' else col.asc())
    if q:
        query = query.where(
            KbnMaster.kbn_code.ilike(f'%{q}%') |
            KbnMaster.kbn_name.ilike(f'%{q}%')
        )
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    kbn_import_uuid = session.get('kbn_import_uuid', '')
    template = 'partials/kbn_table.html' if request.headers.get('HX-Request') else 'maintenance_kbn.html'
    return render_template(
        template,
        kbns=pagination.items,
        pagination=pagination,
        kbn_import_uuid=kbn_import_uuid,
        sort=sort,
        order=order,
        q=q,
    )


# ---- Data Output ----

@main_bp.route('/maintenance/data-output')
@login_required
def data_output():
    return render_template('maintenance_data_output.html')
