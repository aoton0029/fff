from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

ColumnType = Literal["str", "int", "float", "date", "datetime"]


@dataclass
class ImportError:
    row: int
    column: str
    message: str


@dataclass
class ImportResult:
    data: list[Any]
    errors: list[ImportError]


@dataclass
class ColumnConfig:
    col_no: str | int
    label: str
    field: str
    type: ColumnType = "str"
    required: bool = False
    validators: list[Callable[[Any], str | None]] = field(default_factory=list)
    description: str | None = None

@dataclass
class ExcelConfig:
    columns: list[ColumnConfig]
    header_row: int = 1
    sheet: str | int | None = None
