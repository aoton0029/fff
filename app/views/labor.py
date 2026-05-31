from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..models.labor_unit_price import LaborUnitPrice
from ..models.upload_batch import UploadBatch
from ..services.excel_reader import get_format_config
from ..view_models.labor import LaborIndexViewModel

FILE_TYPE = 'labor_transfer'


@main_bp.route('/labor/')
@login_required
def labor_index():
    page = request.args.get('page', 1, type=int)
    vm = LaborIndexViewModel(page)
    if htmx:
        return render_template(
            'partials/batch_table.html',
            batches=vm.batches,
            pagination=vm.pagination,
            file_type=vm.file_type,
        )
    salary_batch = UploadBatch.query.filter_by(file_type='salary').order_by(
        UploadBatch.created_at.desc()
    ).first()
    yr_mo = salary_batch.year_month if salary_batch and salary_batch.year_month else None
    current_unit_price = LaborUnitPrice.query.filter_by(year_month=yr_mo).first() if yr_mo else None
    return render_template(
        'labor.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
        excel_format=get_format_config('labor_transfer'),
        current_unit_price=current_unit_price,
    )
