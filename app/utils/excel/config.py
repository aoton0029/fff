from __future__ import annotations

from pathlib import Path

import yaml

from .types import ColumnConfig, ExcelConfig


def load_config(config: str | Path | dict) -> ExcelConfig:
    if isinstance(config, dict):
        raw = config
    else:
        with open(config, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    return _validate_and_build(raw)


def _validate_and_build(raw: dict) -> ExcelConfig:
    if "columns" not in raw:
        raise ValueError("'columns' is required in config")

    header_row = raw.get("header_row", 1)
    if not isinstance(header_row, int) or header_row < 1:
        raise ValueError(f"'header_row' must be a positive integer, got {header_row!r}")

    columns = []
    for col in raw["columns"]:
        columns.append(ColumnConfig(
            label=col["label"],
            field=col["field"],
            type=col.get("type", "str"),
            required=col.get("required", False),
        ))

    sheet = raw.get("sheet", None)
    return ExcelConfig(columns=columns, header_row=header_row, sheet=sheet)
