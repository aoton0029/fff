from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from ..extensions import htmx, db
from ..forms.upload import UploadForm
from ..models.upload_batch import UploadBatch
from ..models.labor_transfer import LaborTransferData
from ..services.data_importer import import_excel_file

labor_bp = Blueprint('labor', __name__, template_folder='../templates')

PER_PAGE = 20
FILE_TYPE = 'labor_transfer'


@labor_bp.route('/')
@login_required
def index():
    form = UploadForm()
    page = request.args.get('page', 1, type=int)

    query = UploadBatch.query.filter_by(file_type=FILE_TYPE).order_by(UploadBatch.created_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    if htmx:
        return render_template(
            'partials/batch_table.html',
            batches=pagination.items,
            pagination=pagination,
            file_type=FILE_TYPE,
        )

    return render_template(
        'labor/index.html',
        form=form,
        batches=pagination.items,
        pagination=pagination,
        file_type=FILE_TYPE,
    )


@labor_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    form = UploadForm()
    if not form.validate_on_submit():
        errors = [{'row': '-', 'field': f, 'message': '; '.join(errs)} for f, errs in form.errors.items()]
        if htmx:
            return render_template('partials/upload_result.html', success=False, errors=errors), 422
        flash('アップロードフォームにエラーがあります。', 'danger')
        return redirect(url_for('labor.index'))

    result = import_excel_file(form.file.data, FILE_TYPE, current_user.id)

    if htmx:
        page = request.args.get('page', 1, type=int)
        query = UploadBatch.query.filter_by(file_type=FILE_TYPE).order_by(UploadBatch.created_at.desc())
        pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
        return render_template(
            'partials/upload_result.html',
            success=result.success,
            saved_count=result.saved_count,
            errors=result.errors,
            batches=pagination.items,
            pagination=pagination,
            file_type=FILE_TYPE,
        )

    if result.success:
        flash(f'{result.saved_count} 件のデータを保存しました。', 'success')
    else:
        flash('アップロードに失敗しました。', 'danger')
    return redirect(url_for('labor.index'))


@labor_bp.route('/detail/<int:batch_id>')
@login_required
def detail(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=FILE_TYPE).first_or_404()
    records = LaborTransferData.query.filter_by(batch_id=batch_id).all()
    return render_template('partials/labor_detail_modal.html', batch=batch, records=records)


@labor_bp.route('/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def delete(batch_id: int):
    batch = UploadBatch.query.filter_by(id=batch_id, file_type=FILE_TYPE).first_or_404()
    LaborTransferData.query.filter_by(batch_id=batch_id).delete()
    db.session.delete(batch)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    query = UploadBatch.query.filter_by(file_type=FILE_TYPE).order_by(UploadBatch.created_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template(
        'partials/batch_table.html',
        batches=pagination.items,
        pagination=pagination,
        file_type=FILE_TYPE,
    )
