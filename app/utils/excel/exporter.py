from __future__ import annotations

from pathlib import Path

import openpyxl

from .config import load_config


def export_excel(
    data: list,
    config: str | Path | dict,
    output_path: str | Path,
) -> None:
    excel_config = load_config(config)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = excel_config.sheet if isinstance(excel_config.sheet, str) else "Sheet1"

    headers = [col.label for col in excel_config.columns]
    ws.append(headers)

    for instance in data:
        row = [getattr(instance, col.field, None) for col in excel_config.columns]
        ws.append(row)

    wb.save(output_path)
