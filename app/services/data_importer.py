"""Data importer service.

Orchestrates: validate rows → save to DB → return result summary.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError
from flask_login import current_user

from ..extensions import db
from ..services.excel_reader import read_excel
from ..validators.salary import SalaryRow
from ..validators.allocation import AllocationRow
from ..validators.labor_transfer import LaborTransferRow
from ..models.upload_batch import UploadBatch
from ..models.salary import SalaryData
from ..models.allocation import AllocationData
from ..models.labor_transfer import LaborTransferData


@dataclass
class ImportResult:
    success: bool
    saved_count: int = 0
    errors: list[dict] = field(default_factory=list)
    batch_id: int | None = None


def _validate_rows(rows: list[dict], file_type: str) -> tuple[list[Any], list[dict]]:
    """Validate all rows. Returns (valid_models, error_list)."""
    validator_map = {
        'salary': SalaryRow,
        'allocation': AllocationRow,
        'labor_transfer': LaborTransferRow,
    }
    validator_cls = validator_map[file_type]
    valid_models: list[Any] = []
    errors: list[dict] = []

    for row in rows:
        row_num = row.pop('_row', '?')
        try:
            model = validator_cls(**row)
            valid_models.append(model)
        except ValidationError as exc:
            for err in exc.errors():
                errors.append({
                    'row': row_num,
                    'field': ' / '.join(str(loc) for loc in err['loc']),
                    'message': err['msg'],
                })

    return valid_models, errors


def _build_db_record(model: Any, file_type: str, batch_id: int, user_id: int) -> Any:
    common = {'batch_id': batch_id, 'created_by': user_id}
    if file_type == 'salary':
        return SalaryData(
            department_code=model.部署コード,
            base_salary=model.本給,
            ability_salary=model.能力給,
            compensation=model.報酬,
            allowance=model.手当,
            headcount=model.人員数,
            total_salary=model.給与額,
            **common,
        )
    elif file_type == 'allocation':
        return AllocationData(
            district_code=model.地区コード,
            section_code=model.課コード,
            allocation_ratio=model.按分人員数,
            **common,
        )
    elif file_type == 'labor_transfer':
        return LaborTransferData(
            account_code=model.勘定科目コード,
            from_section_code=model.from課コード,
            to_section_code=model.to課コード,
            work_hours=model.作業時間,
            **common,
        )
    raise ValueError(f'未定義のファイル種別: {file_type}')


def import_excel_file(file_storage, file_type: str, user_id: int) -> ImportResult:
    """Process an uploaded FileStorage object.

    Saves to a temp file, reads, validates, persists to DB, then deletes the temp file.
    """
    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        rows = read_excel(tmp_path, file_type)
        if not rows:
            return ImportResult(success=False, errors=[{'row': '-', 'field': '-', 'message': 'データが見つかりませんでした。'}])

        valid_models, errors = _validate_rows(rows, file_type)
        if errors:
            return ImportResult(success=False, errors=errors)

        # Persist
        batch = UploadBatch(
            file_name=file_storage.filename,
            file_type=file_type,
            created_by=user_id,
        )
        db.session.add(batch)
        db.session.flush()  # get batch.id

        records = [_build_db_record(m, file_type, batch.id, user_id) for m in valid_models]
        db.session.bulk_save_objects(records)
        db.session.commit()

        return ImportResult(success=True, saved_count=len(records), batch_id=batch.id)

    except Exception as exc:
        db.session.rollback()
        return ImportResult(success=False, errors=[{'row': '-', 'field': '-', 'message': str(exc)}])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
