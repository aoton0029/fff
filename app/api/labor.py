from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from ..views import main_bp
from ..extensions import htmx, db
from ..forms.upload import UploadForm
from ..models.upload_batch import UploadBatch
from ..models.labor_transfer import LaborTransferData
from ..services.data_importer import import_excel_file

_PER_PAGE = 20
_FILE_TYPE = 'labor_transfer'


@main_bp.route('/labor/upload', methods=['POST'])
@login_required
def labor_upload():
    form = UploadForm()
    if not form.validate_on_submit():
        errors = [{'row': '-', 'field': f, 'message': '; '.join(errs)} for f, errs in form.errors.items()]
        if htmx:
            return render_template('partials/upload_result.html', success=False, errors=errors), 422
        flash('アップロードフォームにエラーがあります。', 'danger')
        return redirect(url_for('main.labor_index'))

    result = import_excel_file(form.file.data, _FILE_TYPE, current_user.id)

    if htmx:
        page = request.args.get('page', 1, type=int)
        query = UploadBatch.query.filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
        pagination = query.paginate(page=page, per_page=_PER_PAGE, error_out=False)
        return render_template(
            'partials/upload_result.html',
            success=result.success,
            saved_count=result.saved_count,
            errors=result.errors,
            batches=pagination.items,
            pagination=pagination,
            file_type=_FILE_TYPE,
        )

    if result.success:
        flash(f'{result.saved_count} 件のデータを保存しました。', 'success')
    else:
        flash('アップロードに失敗しました。', 'danger')
    return redirect(url_for('main.labor_index'))


@main_bp.route('/labor/detail/<int:batch_id>')
@login_required
def labor_detail(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=_FILE_TYPE).first_or_404()
    records = LaborTransferData.query.filter_by(batch_id=batch_id).all()
    return render_template('partials/labor_detail_modal.html', batch=batch, records=records)


@main_bp.route('/labor/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def labor_delete(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=_FILE_TYPE).first_or_404()
    LaborTransferData.query.filter_by(batch_id=batch_id).delete()
    db.session.delete(batch)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    query = UploadBatch.query.filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
    pagination = query.paginate(page=page, per_page=_PER_PAGE, error_out=False)
    return render_template(
        'partials/batch_table.html',
        batches=pagination.items,
        pagination=pagination,
        file_type=_FILE_TYPE,
    )
