import io
import os

import openpyxl
from flask import Response, render_template, request, flash, redirect, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy import delete, select

from ..views import main_bp
from ..extensions import htmx, db
from ..models.dat_processing_month import ProcessingMonth
from ..models.dat_upload_batch import UploadBatch
from ..models.dat_labor_transfer import LaborTransferData
from ..models.dat_labor_unit_price import LaborUnitPrice
from ..services.data_importer import import_excel_file
from ..services.sap_exporter import build_labor_tsv

_PER_PAGE = 20
_FILE_TYPE = 'labor_transfer'
_ALLOWED_EXT = {'.xlsx', '.xls'}


@main_bp.route('/labor/upload', methods=['POST'])
@login_required
def labor_upload():
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
    return redirect(url_for('main.labor_index'))


@main_bp.route('/labor/detail/<int:batch_id>')
@login_required
def labor_detail(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    records = db.session.scalars(select(LaborTransferData).filter_by(batch_id=batch_id)).all()
    return render_template('partials/labor_detail_modal.html', batch=batch, records=records)


@main_bp.route('/labor/sap-output')
@login_required
def labor_sap_output():
    setting = db.session.scalar(select(ProcessingMonth))
    yr_mo = setting.year_month if setting else None
    unit_price_record = (
        db.session.scalar(select(LaborUnitPrice).filter_by(year_month=yr_mo)) if yr_mo else None
    )
    if not unit_price_record:
        flash('労務費単価が登録されていません。先に単価を設定してください。', 'danger')
        return redirect(url_for('main.labor_index'))
    ym_suffix = yr_mo.replace('-', '') if yr_mo else 'unknown'
    filename = f'labor_SAP_{ym_suffix}.txt'
    tsv_bytes = build_labor_tsv(unit_price_record.unit_price)
    return Response(
        tsv_bytes,
        mimetype='text/plain; charset=cp932',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@main_bp.route('/labor/delete/<int:batch_id>', methods=['DELETE', 'POST'])
@login_required
def labor_delete(batch_id: int):
    batch = db.first_or_404(select(UploadBatch).filter_by(id=batch_id, file_type=_FILE_TYPE))
    db.session.execute(delete(LaborTransferData).where(LaborTransferData.batch_id == batch_id))
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


_MOCK_LABOR_CALC_ROWS = [
    {"section_code": "A01", "transfer_code": "T001", "transfer_kbn": "振替", "hours": 160.0, "unit_price": 2500.0, "amount": 400_000},
    {"section_code": "A01", "transfer_code": "T002", "transfer_kbn": "振替", "hours": 80.0,  "unit_price": 2500.0, "amount": 200_000},
    {"section_code": "B02", "transfer_code": "T003", "transfer_kbn": "振替", "hours": 200.0, "unit_price": 2800.0, "amount": 560_000},
    {"section_code": "C03", "transfer_code": "T004", "transfer_kbn": "振替", "hours": 120.0, "unit_price": 3000.0, "amount": 360_000},
]


@main_bp.route('/labor/calc-preview')
@login_required
def labor_calc_preview():
    # TODO: SQLビュー（v_労務費計算）実装後、rows をDBクエリに置換
    rows = _MOCK_LABOR_CALC_ROWS
    return render_template('partials/labor_calc_modal.html', rows=rows)


@main_bp.route('/labor/calc-download')
@login_required
def labor_calc_download():
    # TODO: SQLビュー実装後、rows をDBクエリに置換
    rows = _MOCK_LABOR_CALC_ROWS

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '労務費計算データ'
    ws.append(['課コード', '振替先コード', '振替区分', '時間', '単価', '金額'])
    for row in rows:
        ws.append([
            row['section_code'], row['transfer_code'], row['transfer_kbn'],
            row['hours'], row['unit_price'], row['amount'],
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name='労務費計算データ.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


# ---- Labor Unit Price CRUD ----

@main_bp.route('/labor/unit-price/create', methods=['POST'])
@login_required
def labor_unit_price_create():
    record = LaborUnitPrice(
        year_month=request.form['year_month'].strip(),
        unit_price=float(request.form['unit_price']),
    )
    db.session.add(record)
    try:
        db.session.commit()
        flash('労務費単価を追加しました。', 'success')
    except Exception:
        db.session.rollback()
        flash('同じ年月の単価がすでに存在します。', 'danger')
    return redirect(url_for('main.labor_index'))


@main_bp.route('/labor/unit-price/update/<int:record_id>', methods=['POST'])
@login_required
def labor_unit_price_update(record_id: int):
    record = db.get_or_404(LaborUnitPrice, record_id)
    record.unit_price = float(request.form['unit_price'])
    db.session.commit()
    flash('労務費単価を更新しました。', 'success')
    return redirect(url_for('main.labor_index'))


@main_bp.route('/labor/unit-price/delete/<int:record_id>', methods=['POST'])
@login_required
def labor_unit_price_delete(record_id: int):
    record = db.get_or_404(LaborUnitPrice, record_id)
    db.session.delete(record)
    db.session.commit()
    flash('労務費単価を削除しました。', 'success')
    return redirect(url_for('main.labor_index'))


@main_bp.route('/labor/unit-price/set', methods=['POST'])
@login_required
def labor_unit_price_set():
    """現在の処理年月の労務費単価を upsert する。"""
    year_month = request.form.get('year_month', '').strip()
    unit_price_str = request.form.get('unit_price', '').strip()
    if not year_month or not unit_price_str:
        flash('年月または単価が不正です。', 'danger')
        return redirect(url_for('main.labor_index'))
    try:
        unit_price = float(unit_price_str)
    except ValueError:
        flash('単価は数値で入力してください。', 'danger')
        return redirect(url_for('main.labor_index'))
    record = db.session.scalar(select(LaborUnitPrice).filter_by(year_month=year_month))
    if record:
        record.unit_price = unit_price
    else:
        record = LaborUnitPrice(year_month=year_month, unit_price=unit_price)
        db.session.add(record)
    db.session.commit()
    flash(f'{year_month} の労務費単価を保存しました。', 'success')
    return redirect(url_for('main.labor_index'))
