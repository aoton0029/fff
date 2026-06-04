from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..services.excel_reader import get_format_config
from ..view_models.allocation import AllocationIndexViewModel

FILE_TYPE = 'allocation'


@main_bp.route('/allocation/')
@login_required
def allocation_index():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'created_at')
    sort_dir = request.args.get('order', 'desc')
    vm = AllocationIndexViewModel(page, sort_by, sort_dir)
    if htmx:
        return render_template(
            'partials/batch_table.html',
            batches=vm.batches,
            pagination=vm.pagination,
            file_type=vm.file_type,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    return render_template(
        'allocation.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
        salary_count=vm.salary_count,
        excel_format=get_format_config('allocation'),
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
