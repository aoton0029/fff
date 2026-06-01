from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import delete, select

from ..views import main_bp
from ..extensions import htmx, db
from ..forms.upload import UploadForm
from ..models.upload_batch import UploadBatch
from ..models.salary import SalaryData
from ..services.data_importer import import_excel_file

_FILE_TYPE = 'salary'


@main_bp.route('/salary/upload', methods=['POST'])
@login_required
def salary_upload():
    # Single-batch policy: block upload if batch already exists
    existing = db.session.scalar(select(UploadBatch).filter_by(file_type=_FILE_TYPE))
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

    result = import_excel_file(form.file.data, _FILE_TYPE, current_user.id)

    if htmx:
        batch = db.session.get(UploadBatch, result.batch_id) if result.success else None
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
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    records = db.session.scalars(select(SalaryData).filter_by(batch_id=batch_id)).all()
    return render_template('partials/salary_detail_modal.html', batch=batch, records=records)


@main_bp.route('/salary/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def salary_delete(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    db.session.execute(delete(SalaryData).where(SalaryData.batch_id == batch_id))
    db.session.delete(batch)
    db.session.commit()
    return render_template('partials/salary_upload_result.html', batch=None)

