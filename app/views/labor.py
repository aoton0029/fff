from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..repositories.labor_repository import LaborRepository
from ..services.excel_reader import get_format_config
from ..view_models.labor import LaborIndexViewModel

FILE_TYPE = 'labor_transfer'

_labor_repo = LaborRepository()


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
    setting = _labor_repo.get_current_processing_month()
    yr_mo = setting.year_month if setting else None
    current_unit_price = _labor_repo.get_unit_price(yr_mo) if yr_mo else None
    return render_template(
        'labor.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
        excel_format=get_format_config('labor_transfer'),
        current_unit_price=current_unit_price,
    )
