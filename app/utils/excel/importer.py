from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import openpyxl

from .config import load_config
from .types import ColumnConfig, ExcelConfig, ImportError, ImportResult
from .validator import validate_row


def _coerce(val: Any, col: ColumnConfig) -> Any:
    """Excel cell value を col.type に従って変換する。"""
    if val is None:
        return None
    t = col.type
    if t == "date":
        if isinstance(val, date):
            return val if not isinstance(val, datetime) else val.date()
        # 文字列 "YYYY-MM-DD" などをパース
        s = str(val).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        return s  # パース失敗は validate_row に任せる
    if t == "datetime":
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime(val.year, val.month, val.day)
        return str(val)
    if t == "int":
        try:
            return int(val)
        except (ValueError, TypeError):
            return str(val)
    if t == "float":
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val)
    # str (default)
    return str(val)


def _col_no_to_idx(col_no: str | int) -> int:
    if isinstance(col_no, str):
        return openpyxl.utils.column_index_from_string(col_no) - 1
    return col_no - 1


def import_header_cell(
    file_path: str | Path,
    config: str | Path | dict,
    target_class: type,
    sheet_name: str | int | None = None,
) -> ImportResult:
    excel_config = load_config(config)
    if sheet_name is not None:
        excel_config.sheet = sheet_name
    return _import_excel(file_path, excel_config, target_class)


def import_table(
    file_path: str | Path,
    config: str | Path | dict,
    target_class: type,
    sheet_name: str | int | None = None,
) -> ImportResult:
    excel_config = load_config(config)
    excel_config.header_row = 1
    if sheet_name is not None:
        excel_config.sheet = sheet_name
    return _import_excel(file_path, excel_config, target_class)


def _import_excel(
    file_path: str | Path,
    excel_config: ExcelConfig,
    target_class: type,
) -> ImportResult:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    sheet = excel_config.sheet if excel_config.sheet is not None else 0
    if isinstance(sheet, str):
        ws = wb[sheet]
    else:
        ws = wb.worksheets[sheet]

    all_rows = list(ws.iter_rows(values_only=True))
    header_row_idx = excel_config.header_row - 1

    if header_row_idx >= len(all_rows):
        return ImportResult(data=[], errors=[])

    data = []
    errors = []

    data_rows = all_rows[header_row_idx + 1:]
    consecutive_empty = 0
    for row_offset, row_values in enumerate(data_rows):
        actual_row_num = excel_config.header_row + 1 + row_offset

        if all(v is None for v in row_values):
            consecutive_empty += 1
            if consecutive_empty >= 2:
                break
            continue

        consecutive_empty = 0

        row_data: dict[str, Any] = {}
        for col in excel_config.columns:
            idx = _col_no_to_idx(col.col_no)
            val = row_values[idx] if idx < len(row_values) else None
            row_data[col.label] = _coerce(val, col)

        row_errors = validate_row(row_data, excel_config.columns, actual_row_num)
        errors.extend(row_errors)

        if not row_errors:
            kwargs = {}
            for col in excel_config.columns:
                kwargs[col.field] = row_data.get(col.label)
            data.append(target_class(**kwargs))

    return ImportResult(data=data, errors=errors)
