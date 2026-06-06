from __future__ import annotations

from pathlib import Path
from typing import Any

import openpyxl

from .config import load_config
from .types import ExcelConfig, ImportError, ImportResult
from .validator import validate_row


def import_header_cell(
    file_path: str | Path,
    config: str | Path | dict,
    target_class: type,
) -> ImportResult:
    excel_config = load_config(config)
    return _import_excel(file_path, excel_config, target_class)


def import_table(
    file_path: str | Path,
    config: str | Path | dict,
    target_class: type,
) -> ImportResult:
    excel_config = load_config(config)
    excel_config.header_row = 1
    return _import_excel(file_path, excel_config, target_class)


def _import_excel(
    file_path: str | Path,
    excel_config: ExcelConfig,
    target_class: type,
) -> ImportResult:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    wb = openpyxl.load_workbook(path)
    sheet = excel_config.sheet if excel_config.sheet is not None else 0
    if isinstance(sheet, str):
        ws = wb[sheet]
    else:
        ws = wb.worksheets[sheet]

    all_rows = list(ws.iter_rows(values_only=True))
    header_row_idx = excel_config.header_row - 1

    if header_row_idx >= len(all_rows):
        return ImportResult(data=[], errors=[])

    header_cells = all_rows[header_row_idx]
    header_map: dict[str, int] = {}
    for i, cell in enumerate(header_cells):
        if cell is not None:
            header_map[str(cell)] = i

    missing_labels = [col.label for col in excel_config.columns if col.label not in header_map]

    data = []
    errors = []

    data_rows = all_rows[header_row_idx + 1:]
    for row_offset, row_values in enumerate(data_rows):
        actual_row_num = excel_config.header_row + 1 + row_offset

        if all(v is None for v in row_values):
            continue

        row_data: dict[str, Any] = {}
        for col in excel_config.columns:
            if col.label in header_map:
                idx = header_map[col.label]
                val = row_values[idx] if idx < len(row_values) else None
                row_data[col.label] = str(val) if val is not None else None
            else:
                row_data[col.label] = None

        for label in missing_labels:
            errors.append(ImportError(
                row=actual_row_num,
                column=label,
                message=f"列 '{label}' がExcelに存在しません",
            ))

        row_errors = validate_row(row_data, excel_config.columns, actual_row_num)
        errors.extend(row_errors)

        if not row_errors and not missing_labels:
            kwargs = {}
            for col in excel_config.columns:
                kwargs[col.field] = row_data.get(col.label)
            data.append(target_class(**kwargs))

    return ImportResult(data=data, errors=errors)
