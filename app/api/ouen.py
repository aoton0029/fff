import os

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import delete, select

from ..views import main_bp
from ..extensions import htmx, db
from ..models.upload_batch import UploadBatch
from ..models.ouen import OuenData
from ..services.data_importer import import_excel_file

_PER_PAGE = 20
_FILE_TYPE = 'ouen'
_ALLOWED_EXT = {'.xlsx', '.xls'}


@main_bp.route('/ouen/upload', methods=['POST'])
@login_required
def ouen_upload():
    files = [f for f in request.files.getlist('file') if f and f.filename]
    file_results = None
    global_error = None

    if not files:
        global_error = 'ファイルを選択してください。'
    else:
        bad = [f.filename for f in files if os.path.splitext(f.filename)[1].lower() not in _ALLOWED_EXT]
        if bad:
            global_error = f'Excelファイル(.xlsx/.xls)のみアップロードできます: {", ".join(bad)}'
        else:
            file_results = []
            for f in files:
                result = import_excel_file(f, _FILE_TYPE, current_user.id)
                file_results.append({
                    'filename': f.filename,
                    'success': result.success,
                    'saved_count': result.saved_count,
                    'errors': result.errors,
                })

    if htmx:
        page = request.args.get('page', 1, type=int)
        query = select(UploadBatch).filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
        pagination = db.paginate(query, page=page, per_page=_PER_PAGE, error_out=False)
        return render_template(
            'partials/ouen_upload_result.html',
            file_results=file_results,
            global_error=global_error,
            batches=pagination.items,
            pagination=pagination,
        )

    if global_error:
        flash(global_error, 'danger')
    elif file_results:
        total_saved = sum(r['saved_count'] for r in file_results if r['success'])
        success_count = sum(1 for r in file_results if r['success'])
        if success_count == len(file_results):
            flash(f'{total_saved}件のデータを保存しました。', 'success')
        elif success_count > 0:
            flash(f'{success_count}/{len(file_results)}ファイルが成功しました。', 'warning')
        else:
            flash('アップロードに失敗しました。', 'danger')
    return redirect(url_for('main.ouen_index'))


@main_bp.route('/ouen/detail/<int:batch_id>')
@login_required
def ouen_detail(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    records = db.session.scalars(select(OuenData).filter_by(batch_id=batch_id)).all()
    return render_template('partials/ouen_detail_modal.html', batch=batch, records=records)


@main_bp.route('/ouen/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def ouen_delete(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    db.session.execute(delete(OuenData).where(OuenData.batch_id == batch_id))
    db.session.delete(batch)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    query = select(UploadBatch).filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
    pagination = db.paginate(query, page=page, per_page=_PER_PAGE, error_out=False)
    return render_template(
        'partials/ouen_batch_table.html',
        batches=pagination.items,
        pagination=pagination,
    )
