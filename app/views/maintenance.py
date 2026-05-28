from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required
import io
import csv

from ..extensions import db
from ..models.section import SectionMaster
from ..models.department import DepartmentMaster
from ..models.salary import SalaryData
from ..models.allocation import AllocationData
from ..models.labor_transfer import LaborTransferData

maintenance_bp = Blueprint('maintenance', __name__, template_folder='../templates')

PER_PAGE = 30


# ---- Section Master ----

@maintenance_bp.route('/section')
@login_required
def section_list():
    page = request.args.get('page', 1, type=int)
    query = SectionMaster.query.order_by(SectionMaster.section_code)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('maintenance/section.html', sections=pagination.items, pagination=pagination)


@maintenance_bp.route('/section/create', methods=['POST'])
@login_required
def section_create():
    section = SectionMaster(
        section_code=request.form['section_code'].strip(),
        section_name=request.form['section_name'].strip(),
        district_code=request.form['district_code'].strip(),
        cost_center_code=request.form['cost_center_code'].strip(),
    )
    db.session.add(section)
    try:
        db.session.commit()
        flash('課マスタを追加しました。', 'success')
    except Exception:
        db.session.rollback()
        flash('課コードが重複しています。', 'danger')
    return redirect(url_for('maintenance.section_list'))


@maintenance_bp.route('/section/update/<section_code>', methods=['POST'])
@login_required
def section_update(section_code: str):
    section = SectionMaster.query.get_or_404(section_code)
    section.section_name = request.form['section_name'].strip()
    section.district_code = request.form['district_code'].strip()
    section.cost_center_code = request.form['cost_center_code'].strip()
    db.session.commit()
    flash('課マスタを更新しました。', 'success')
    return redirect(url_for('maintenance.section_list'))


@maintenance_bp.route('/section/delete/<section_code>', methods=['POST'])
@login_required
def section_delete(section_code: str):
    section = SectionMaster.query.get_or_404(section_code)
    db.session.delete(section)
    db.session.commit()
    flash('課マスタを削除しました。', 'success')
    return redirect(url_for('maintenance.section_list'))


# ---- Department Master ----

@maintenance_bp.route('/department')
@login_required
def department_list():
    page = request.args.get('page', 1, type=int)
    query = DepartmentMaster.query.order_by(DepartmentMaster.department_code)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('maintenance/department.html', departments=pagination.items, pagination=pagination)


@maintenance_bp.route('/department/create', methods=['POST'])
@login_required
def department_create():
    dept = DepartmentMaster(
        department_code=request.form['department_code'].strip(),
        department_name=request.form['department_name'].strip(),
        district_code=request.form['district_code'].strip(),
        section_code=request.form['section_code'].strip(),
        account_code=request.form['account_code'].strip(),
        cost_center_code=request.form['cost_center_code'].strip(),
    )
    db.session.add(dept)
    try:
        db.session.commit()
        flash('部署マスタを追加しました。', 'success')
    except Exception:
        db.session.rollback()
        flash('部署コードが重複しています。', 'danger')
    return redirect(url_for('maintenance.department_list'))


@maintenance_bp.route('/department/update/<department_code>', methods=['POST'])
@login_required
def department_update(department_code: str):
    dept = DepartmentMaster.query.get_or_404(department_code)
    dept.department_name = request.form['department_name'].strip()
    dept.district_code = request.form['district_code'].strip()
    dept.section_code = request.form['section_code'].strip()
    dept.account_code = request.form['account_code'].strip()
    dept.cost_center_code = request.form['cost_center_code'].strip()
    db.session.commit()
    flash('部署マスタを更新しました。', 'success')
    return redirect(url_for('maintenance.department_list'))


@maintenance_bp.route('/department/delete/<department_code>', methods=['POST'])
@login_required
def department_delete(department_code: str):
    dept = DepartmentMaster.query.get_or_404(department_code)
    db.session.delete(dept)
    db.session.commit()
    flash('部署マスタを削除しました。', 'success')
    return redirect(url_for('maintenance.department_list'))


# ---- Data Output ----

@maintenance_bp.route('/data-output')
@login_required
def data_output():
    return render_template('maintenance/data_output.html')


@maintenance_bp.route('/data-output/download/<table_name>')
@login_required
def data_output_download(table_name: str):
    allowed = {
        'salary': (SalaryData, ['id', 'batch_id', 'department_code', 'base_salary', 'ability_salary', 'compensation', 'allowance', 'headcount', 'total_salary', 'created_at', 'created_by']),
        'allocation': (AllocationData, ['id', 'batch_id', 'district_code', 'section_code', 'allocation_ratio', 'created_at', 'created_by']),
        'labor_transfer': (LaborTransferData, ['id', 'batch_id', 'account_code', 'from_section_code', 'to_section_code', 'work_hours', 'created_at', 'created_by']),
        'section': (SectionMaster, ['section_code', 'section_name', 'district_code', 'cost_center_code']),
        'department': (DepartmentMaster, ['department_code', 'department_name', 'district_code', 'section_code', 'account_code', 'cost_center_code']),
    }

    if table_name not in allowed:
        flash('無効なテーブルです。', 'danger')
        return redirect(url_for('maintenance.data_output'))

    model_cls, columns = allowed[table_name]
    records = model_cls.query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for rec in records:
        writer.writerow([getattr(rec, col, '') for col in columns])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{table_name}.csv',
    )
