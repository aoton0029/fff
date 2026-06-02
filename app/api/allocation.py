import io
import os

import openpyxl
from flask import Response, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from sqlalchemy import delete, select

from ..views import main_bp
from ..extensions import htmx, db
from ..models.dat_processing_month import ProcessingMonth
from ..models.dat_upload_batch import UploadBatch
from ..models.dat_allocation import AllocationData
from ..services.data_importer import import_excel_file
from ..services.sap_exporter import build_allocation_tsv

_PER_PAGE = 20
_FILE_TYPE = 'allocation'
_ALLOWED_EXT = {'.xlsx', '.xls'}


@main_bp.route('/allocation/upload', methods=['POST'])
@login_required
def allocation_upload():
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
            'partials/upload_result.html',
            file_results=file_results,
            global_error=global_error,
            batches=pagination.items,
            pagination=pagination,
            file_type=_FILE_TYPE,
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
    return redirect(url_for('main.allocation_index'))


@main_bp.route('/allocation/detail/<int:batch_id>')
@login_required
def allocation_detail(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    records = db.session.scalars(select(AllocationData).filter_by(batch_id=batch_id)).all()
    return render_template('partials/allocation_detail_modal.html', batch=batch, records=records)


@main_bp.route('/allocation/sap-output')
@login_required
def allocation_sap_output():
    setting = db.session.scalar(select(ProcessingMonth))
    yr_mo = setting.year_month if setting else None
    ym_suffix = yr_mo.replace('-', '') if yr_mo else 'unknown'
    filename = f'allocation_SAP_{ym_suffix}.txt'
    tsv_bytes = build_allocation_tsv()
    return Response(
        tsv_bytes,
        mimetype='text/plain; charset=cp932',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


_MOCK_CALC_ROWS = [
    {"section_code": "A01", "process_code": "P001", "process_name": "工程A", "formation": 10.0, "fixed_count": 2.0, "days": 20.0, "amount": 1_200_000},
    {"section_code": "A01", "process_code": "P002", "process_name": "工程B", "formation": 8.0,  "fixed_count": 1.0, "days": 18.0, "amount":   980_000},
    {"section_code": "B02", "process_code": "P003", "process_name": "工程C", "formation": 12.0, "fixed_count": 3.0, "days": 22.0, "amount": 1_450_000},
    {"section_code": "B02", "process_code": "P004", "process_name": "工程D", "formation": 6.0,  "fixed_count": 0.0, "days": 15.0, "amount":   670_000},
]


@main_bp.route('/allocation/calc-preview')
@login_required
def allocation_calc_preview():
    # TODO: SQLビュー（v_工程配賦計算）実装後、rows をDBクエリに置換
    rows = _MOCK_CALC_ROWS
    return render_template('partials/allocation_calc_modal.html', rows=rows)


@main_bp.route('/allocation/calc-download')
@login_required
def allocation_calc_download():
    # TODO: SQLビュー実装後、rows をDBクエリに置換
    rows = _MOCK_CALC_ROWS

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '工程配賦計算データ'
    headers = ['課コード', '工程コード', '工程名', '編成', '固定', '日数', '按分額']
    ws.append(headers)
    for row in rows:
        ws.append([
            row['section_code'], row['process_code'], row['process_name'],
            row['formation'], row['fixed_count'], row['days'], row['amount'],
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name='工程配賦計算データ.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@main_bp.route('/allocation/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def allocation_delete(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    db.session.execute(delete(AllocationData).where(AllocationData.batch_id == batch_id))
    db.session.delete(batch)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    query = select(UploadBatch).filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
    pagination = db.paginate(query, page=page, per_page=_PER_PAGE, error_out=False)
    return render_template(
        'partials/batch_table.html',
        batches=pagination.items,
        pagination=pagination,
        file_type=_FILE_TYPE,
    )
