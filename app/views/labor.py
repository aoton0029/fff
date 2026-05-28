from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
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
    return render_template(
        'labor.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
    )
