"""Master data import service.

Reads an Excel file (first row = headers), validates every row with Pydantic,
checks for intra-file duplicate primary keys and row-count reduction warnings.

Returns a MasterImportResult that callers use to decide whether to persist,
ask for confirmation, or surface errors to the user.
"""
from __future__ import annotations

import io
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import openpyxl
from pydantic import ValidationError
from werkzeug.datastructures import FileStorage

from ..validators.master import DepartmentMasterRow, SectionMasterRow

_SECTION_COLS = ['section_code', 'section_name', 'district_code', 'cost_center_code']
_DEPARTMENT_COLS = [
    'department_code',
    'department_name',
    'district_code',
    'section_code',
    'agg_section_code',
    'kbn_code',
    'account_code',
    'cost_center_code',
]

_UPLOADS_DIR = Path(__file__).parent.parent.parent / 'instance' / 'uploads'


@dataclass
class MasterImportResult:
    rows: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_rows(file_storage: FileStorage, expected_cols: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Read Excel rows (openpyxl). Returns (rows, errors)."""
    errors: list[str] = []
    data = file_storage.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception as exc:
        return [], [f'Excelファイルを開けませんでした: {exc}']

    ws = wb.worksheets[0]
    rows_iter = ws.iter_rows(values_only=True)

    # Header row
    try:
        header_row = next(rows_iter)
    except StopIteration:
        wb.close()
        return [], ['ファイルにデータがありません。']

    actual_cols = [str(c).strip() if c is not None else '' for c in header_row]

    # Trim trailing empty columns to allow extra blank columns on the right
    while actual_cols and actual_cols[-1] == '':
        actual_cols.pop()

    if actual_cols != expected_cols:
        wb.close()
        return [], [
            f'列名が一致しません。\n期待: {expected_cols}\n実際: {actual_cols}'
        ]

    rows: list[dict[str, Any]] = []
    for row in rows_iter:
        # Skip entirely blank rows
        if all(c is None or str(c).strip() == '' for c in row):
            continue
        record = {col: row[i] for i, col in enumerate(expected_cols)}
        rows.append(record)

    wb.close()
    return rows, errors


def _validate_rows(rows: list[dict[str, Any]], model_cls: type, pk_col: str) -> tuple[list[dict[str, str]], list[str]]:
    """Validate each row with Pydantic. Returns (valid_rows, errors)."""
    errors: list[str] = []
    valid: list[dict[str, str]] = []

    for idx, raw in enumerate(rows, start=2):  # row 1 is header
        try:
            obj = model_cls.model_validate(raw)
            valid.append(obj.model_dump())
        except ValidationError as exc:
            for e in exc.errors():
                loc = e['loc'][0] if e['loc'] else '?'
                msg = e['msg']
                errors.append(f'行{idx}: {loc} — {msg}')

    return valid, errors


def _check_duplicates(valid_rows: list[dict[str, str]], pk_col: str) -> list[str]:
    """Detect duplicate primary key values within the file."""
    seen: dict[str, int] = {}
    errors: list[str] = []
    for idx, row in enumerate(valid_rows, start=2):
        key = row.get(pk_col, '')
        if key in seen:
            errors.append(f'行{seen[key]}/行{idx}: {key} が重複しています')
        else:
            seen[key] = idx
    return errors


def _build_result(
    file_storage: FileStorage,
    expected_cols: list[str],
    model_cls: type,
    pk_col: str,
    current_count: int,
) -> MasterImportResult:
    result = MasterImportResult()

    rows_raw, read_errors = _read_rows(file_storage, expected_cols)
    if read_errors:
        result.errors.extend(read_errors)
        return result

    if not rows_raw:
        result.errors.append('取り込みデータがありません。')
        return result

    valid_rows, val_errors = _validate_rows(rows_raw, model_cls, pk_col)
    result.errors.extend(val_errors)

    if not result.errors:
        dup_errors = _check_duplicates(valid_rows, pk_col)
        result.errors.extend(dup_errors)

    if not result.errors:
        result.rows = valid_rows
        # Row-count warning: any reduction triggers a warning
        if current_count > 0 and len(valid_rows) < current_count:
            result.warnings.append(
                f'現在 {current_count} 件 → {len(valid_rows)} 件に減少します。本当に取り込みますか？'
            )

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def read_and_validate_section(file_storage: FileStorage, current_count: int) -> MasterImportResult:
    """Validate the uploaded section master Excel file."""
    return _build_result(file_storage, _SECTION_COLS, SectionMasterRow, 'section_code', current_count)


def read_and_validate_department(file_storage: FileStorage, current_count: int) -> MasterImportResult:
    """Validate the uploaded department master Excel file."""
    return _build_result(file_storage, _DEPARTMENT_COLS, DepartmentMasterRow, 'department_code', current_count)


def save_pending(rows: list[dict[str, str]], master_type: str) -> str:
    """Persist validated rows to a temp JSON file. Returns the UUID token."""
    _UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    path = _UPLOADS_DIR / f'master_{master_type}_{token}.json'
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding='utf-8')
    return token


def load_pending(token: str, master_type: str) -> list[dict[str, str]] | None:
    """Load rows from a temp JSON file. Returns None if not found."""
    path = _UPLOADS_DIR / f'master_{master_type}_{token}.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    return data


def delete_pending(token: str, master_type: str) -> None:
    """Delete the temp JSON file (best-effort)."""
    path = _UPLOADS_DIR / f'master_{master_type}_{token}.json'
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
