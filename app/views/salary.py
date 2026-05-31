from flask import render_template
from flask_login import login_required

from . import main_bp
from ..view_models.salary import SalaryIndexViewModel


@main_bp.route('/salary/')
@login_required
def salary_index():
    vm = SalaryIndexViewModel()
    return render_template(
        'salary.html',
        form=vm.form,
        batch=vm.batch,
        file_type=vm.file_type,
    )
