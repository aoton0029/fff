from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timezone
from sqlalchemy import delete, select

from . import main_bp
from ..extensions import db
from ..models.dat_salary import SalaryData
from ..models.dat_allocation import AllocationData
from ..models.dat_labor_transfer import LaborTransferData
from ..models.dat_ouen import OuenData
from ..models.dat_upload_batch import UploadBatch
from ..models.dat_processing_month import ProcessingMonth


@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@main_bp.route('/clear-all-data', methods=['POST'])
@login_required
def clear_all_data():
    """全トランデータ削除 + 処理年月保存（マスタ・労務費単価は尊重）。"""
    year_month = request.form.get('year_month', '').strip()
    if not year_month:
        flash('処理年月を選択してください。', 'danger')
        return redirect(url_for('main.index'))

    db.session.execute(delete(SalaryData))
    db.session.execute(delete(AllocationData))
    db.session.execute(delete(LaborTransferData))
    db.session.execute(delete(OuenData))
    db.session.execute(delete(UploadBatch))

    setting = db.session.scalar(select(ProcessingMonth))
    if setting:
        setting.year_month = year_month
        setting.updated_at = datetime.now(timezone.utc)
        setting.updated_by = current_user.id
    else:
        db.session.add(ProcessingMonth(
            year_month=year_month,
            updated_by=current_user.id,
        ))
    db.session.commit()
    flash(f'{year_month} の月次処理を開始しました。', 'success')
    return redirect(url_for('main.index'))
