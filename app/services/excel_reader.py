"""Excel reader service.

Reads an Excel file according to a format spec loaded from excel_formats.yaml.
Returns a list of dicts (one per data row). Raises ValueError on format errors.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
import openpyxl
from openpyxl.utils import column_index_from_string


_YAML_PATH = Path(__file__).parent.parent.parent / 'config' / 'excel_formats.yaml'


def _load_formats() -> dict:
    with open(_YAML_PATH, encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_format_config(file_type: str) -> dict:
    """excel_formats

    Args:
        file_type (str): 'salary' | 'ouen' | 'allocation' | 'labor'

    Raises:
        ValueError: 

    Returns:
        dict: 
    """
    formats = _load_formats()
    if file_type not in formats:
        raise ValueError(f'未定義のファイル種別です: {file_type}')
    return formats[file_type]


def read_excel(file_path: str | os.PathLike, file_type: str) -> list[dict[str, Any]]:
    """エクセル読み込み

    Args:
        file_path: パス (tmpファイル).
        file_type: excel_formats.yamlのキー ('salary' | 'ouen' | 'allocation' | 'labor').

    Returns:
        カラムのリスト

    Raises:
        ValueError: シートなし / データなし
    """
    fmt = get_format_config(file_type)
    sheet_name: str = fmt['sheet_name']
    header_row: int = fmt['header_row']
    use_cols: str = fmt['use_cols']  # e.g. "A:G"
    columns: list[dict] = fmt['columns']

    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    try:
        if sheet_name not in wb.sheetnames:
            raise ValueError(f'シート "{sheet_name}" が見つかりません。')

        ws = wb[sheet_name]

        # Determine column range
        col_start_str, col_end_str = use_cols.split(':')
        col_start = column_index_from_string(col_start_str)
        col_end = column_index_from_string(col_end_str)

        column_names = [c['name'] for c in columns]
        data_rows: list[dict[str, Any]] = []

        for row_idx, row in enumerate(ws.iter_rows(min_row=header_row + 1, min_col=col_start, max_col=col_end, values_only=True), start=header_row + 1):
            # Skip entirely empty rows
            if all(cell is None or str(cell).strip() == '' for cell in row):
                continue

            record: dict[str, Any] = {}
            for col_name, cell_value in zip(column_names, row):
                record[col_name] = cell_value
            record['_row'] = row_idx
            data_rows.append(record)

        return data_rows
    finally:
        wb.close()
