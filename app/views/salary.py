from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..view_models.salary import SalaryIndexViewModel

FILE_TYPE = 'salary'


@main_bp.route('/salary/')
@login_required
def salary_index():
    page = request.args.get('page', 1, type=int)
    vm = SalaryIndexViewModel(page)
    if htmx:
        return render_template(
            'partials/batch_table.html',
            batches=vm.batches,
            pagination=vm.pagination,
            file_type=vm.file_type,
        )
    return render_template(
        'salary.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        file_type=vm.file_type,
    )
