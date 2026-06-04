from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import delete, select

from ..views import main_bp
from ..extensions import htmx, db
from ..forms.upload import UploadForm
from ..models.dat_upload_batch import UploadBatch
from ..models.dat_salary import SalaryData
from ..repositories.salary_repository import SalaryRepository
from ..services.data_importer import import_excel_file

_FILE_TYPE = 'salary'

_salary_repo = SalaryRepository()


@main_bp.route('/salary/upload', methods=['POST'])
@login_required
def salary_upload():
    """
    給与データアップロード
    ---
    tags:
      - 給与管理
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: 給与データExcelファイル
    responses:
      200:
        description: アップロード成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            saved_count:
              type: integer
            batch_id:
              type: integer
      400:
        description: バリデーションエラー
    security:
      - Bearer: []
    """
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

    # バリデーションエラー（行レベル）があった場合はエラーバッチをDBに保存して状態を永続化
    error_batch = None
    if not result.success and result.validation_error_count > 0:
        error_batch = UploadBatch(
            file_name=form.file.data.filename,
            file_type=_FILE_TYPE,
            created_by=current_user.id,
            record_count=0,
            error_count=result.validation_error_count,
        )
        db.session.add(error_batch)
        db.session.commit()

    if htmx:
        batch = db.session.get(UploadBatch, result.batch_id) if result.success else error_batch
        return render_template(
            'partials/salary_upload_result.html',
            success=result.success,
            saved_count=result.saved_count,
            errors=result.errors,
            batch=batch,
        )

    if result.success:
        flash(f'{result.saved_count} 件のデータを保存しました。', 'success')
    elif result.validation_error_count > 0:
        flash(f'バリデーションエラーが {result.validation_error_count} 件あります。データを修正して再アップロードしてください。', 'danger')
    else:
        flash('アップロードに失敗しました。', 'danger')
    return redirect(url_for('main.salary_index'))


@main_bp.route('/salary/detail/<int:batch_id>')
@login_required
def salary_detail(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    records = _salary_repo.get_records_by_batch(batch_id)
    return render_template('partials/salary_detail_modal.html', batch=batch, records=records)


@main_bp.route('/salary/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def salary_delete(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    db.session.execute(delete(SalaryData).where(SalaryData.batch_id == batch_id))
    db.session.delete(batch)
    db.session.commit()
    return render_template('partials/salary_upload_result.html', batch=None)

