from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..view_models.allocation import AllocationIndexViewModel

FILE_TYPE = 'allocation'


@main_bp.route('/allocation/')
@login_required
def allocation_index():
    page = request.args.get('page', 1, type=int)
    vm = AllocationIndexViewModel(page)
    if htmx:
        return render_template(
            'partials/batch_table.html',
            batches=vm.batches,
            pagination=vm.pagination,
            file_type=vm.file_type,
        )
    return render_template(
        'allocation.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
    )
