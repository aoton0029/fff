from __future__ import annotations

from datetime import datetime
from typing import Any

from .types import ColumnConfig
from .types import ImportError


def validate_row(
    row_data: dict[str, Any],
    columns: list[ColumnConfig],
    row_num: int,
) -> list[ImportError]:
    errors = []
    for col in columns:
        value = row_data.get(col.label)

        is_empty = value is None or (isinstance(value, str) and value.strip() == "")

        if col.required and is_empty:
            errors.append(ImportError(row=row_num, column=col.label, message="必須項目が未入力です"))
            continue

        if not is_empty and col.type != "str":
            type_error = _check_type(value, col.type)
            if type_error:
                errors.append(ImportError(row=row_num, column=col.label, message=type_error))

        for validator_fn in col.validators:
            try:
                result = validator_fn(value)
                if result is not None:
                    errors.append(ImportError(row=row_num, column=col.label, message=result))
            except Exception as e:
                errors.append(ImportError(row=row_num, column=col.label, message=str(e)))

    return errors


def _check_type(value: Any, col_type: str) -> str | None:
    str_value = str(value)
    try:
        if col_type == "int":
            int(str_value)
        elif col_type == "float":
            float(str_value)
        elif col_type == "date":
            datetime.strptime(str_value, "%Y-%m-%d")
        elif col_type == "datetime":
            datetime.fromisoformat(str_value)
        return None
    except (ValueError, TypeError):
        return f"'{value}' は {col_type} 型に変換できません"
