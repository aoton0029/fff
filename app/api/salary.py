from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from ..views import main_bp
from ..extensions import htmx, db
from ..forms.upload import UploadForm
from ..models.upload_batch import UploadBatch
from ..models.salary import SalaryData
from ..models.processing_month import ProcessingMonth
from ..services.data_importer import import_excel_file

_FILE_TYPE = 'salary'


@main_bp.route('/salary/upload', methods=['POST'])
@login_required
def salary_upload():
    # Single-batch policy: block upload if batch already exists
    existing = UploadBatch.query.filter_by(file_type=_FILE_TYPE).first()
    if existing:
        if htmx:
            return render_template(
                'partials/salary_upload_result.html',
                batch=existing,
                already_exists=True,
            )
        flash('既存の給与データを削除してから再度取り込んでください。', 'warning')
        return redirect(url_for('main.salary_index'))

    form = UploadForm()
    if not form.validate_on_submit():
        errors = [{'row': '-', 'field': f, 'message': '; '.join(errs)} for f, errs in form.errors.items()]
        if htmx:
            return render_template(
                'partials/salary_upload_result.html',
                success=False,
                errors=errors,
                batch=None,
            )
        flash('アップロードフォームにエラーがあります。', 'danger')
        return redirect(url_for('main.salary_index'))

    setting = ProcessingMonth.query.first()
    year_month = setting.year_month if setting else None
    result = import_excel_file(form.file.data, _FILE_TYPE, current_user.id, year_month=year_month)

    if htmx:
        batch = UploadBatch.query.get(result.batch_id) if result.success else None
        return render_template(
            'partials/salary_upload_result.html',
            success=result.success,
            saved_count=result.saved_count,
            errors=result.errors,
            batch=batch,
        )

    if result.success:
        flash(f'{result.saved_count} 件のデータを保存しました。', 'success')
    else:
        flash('アップロードに失敗しました。', 'danger')
    return redirect(url_for('main.salary_index'))


@main_bp.route('/salary/detail/<int:batch_id>')
@login_required
def salary_detail(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=_FILE_TYPE).first_or_404()
    records = SalaryData.query.filter_by(batch_id=batch_id).all()
    return render_template('partials/salary_detail_modal.html', batch=batch, records=records)


@main_bp.route('/salary/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def salary_delete(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=_FILE_TYPE).first_or_404()
    SalaryData.query.filter_by(batch_id=batch_id).delete()
    db.session.delete(batch)
    db.session.commit()
    return render_template('partials/salary_upload_result.html', batch=None)

