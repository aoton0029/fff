from flask import render_template, request
from flask_login import login_required

from . import main_bp
from ..extensions import htmx
from ..services.excel_reader import get_format_config
from ..view_models.ouen import OuenIndexViewModel

_PER_PAGE = 20


@main_bp.route('/ouen/')
@login_required
def ouen_index():
    page = request.args.get('page', 1, type=int)
    vm = OuenIndexViewModel(page)
    if htmx:
        return render_template(
            'partials/ouen_batch_table.html',
            batches=vm.batches,
            pagination=vm.pagination,
        )
    return render_template(
        'ouen.html',
        form=vm.form,
        batches=vm.batches,
        pagination=vm.pagination,
        salary_count=vm.salary_count,
        excel_format=get_format_config('ouen'),
    )