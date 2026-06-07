"""Data importer service.

Orchestrates: read & validate via excel utils → save to DB → return result summary.
"""
from __future__ import annotations

import os
import pickle
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from werkzeug.datastructures import FileStorage

from app.utils.excel.types import ColumnConfig, ExcelConfig

from ..extensions import db
from ..utils.excel import import_header_cell, import_table
from ..models.dat_upload_batch import UploadBatch
from ..models import (
    SalaryData, OuenData, AllocationData, LaborTransferData,
)

_FORMATS_PATH = Path(__file__).parent.parent.parent / "config" / "excel_formats.yaml"

_DATA_MODEL_MAP = {
    'salary':         SalaryData,
    'ouen':           OuenData,
    'allocation':     AllocationData,
    'labor_transfer': LaborTransferData,
}


def _load_formats() -> dict:
    with open(_FORMATS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class ImportResult:
    success: bool
    saved_count: int = 0
    errors: list[dict] = field(default_factory=list)
    batch_id: int | None = None
    validation_error_count: int = 0


@dataclass
class MasterReadResult:
    ok: bool
    rows: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)


def import_excel_file(file_storage: FileStorage, file_type: str, user_id: int) -> ImportResult:
    """業務データ（給与/応援/工程配賦/労務費）をExcelからインポートする。"""
    formats = _load_formats()
    if file_type not in formats:
        return ImportResult(
            success=False,
            errors=[{"row": "-", "field": "-", "message": f"不明なファイル種別: {file_type}"}],
        )

    config_dict = formats[file_type]
    sheet_name = config_dict.get("sheet", 0)
    ModelClass = _DATA_MODEL_MAP[file_type]

    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        result = import_header_cell(tmp_path, config_dict, ModelClass, sheet_name=sheet_name)

        if not result.data and not result.errors:
            return ImportResult(
                success=False,
                errors=[{"row": "-", "field": "-", "message": "データが見つかりませんでした。"}],
            )

        if result.errors:
            errors = [
                {"row": e.row, "field": e.column, "message": e.message}
                for e in result.errors
            ]
            return ImportResult(
                success=False,
                errors=errors,
                validation_error_count=len(errors),
            )

        batch = UploadBatch(
            file_name=file_storage.filename,
            file_type=file_type,
            created_by=user_id,
        )
        db.session.add(batch)
        db.session.flush()

        for obj in result.data:
            obj.batch_id = batch.id
            obj.created_by = user_id

        db.session.bulk_save_objects(result.data)
        batch.record_count = len(result.data)
        db.session.commit()

        return ImportResult(success=True, saved_count=len(result.data), batch_id=batch.id)

    except Exception as exc:
        db.session.rollback()
        return ImportResult(
            success=False,
            errors=[{"row": "-", "field": "-", "message": str(exc)}],
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def import_mst_excel_file(
    file_storage: FileStorage,
    user_id: int,
    model_class: type,
    fmt_key: str,
) -> ImportResult:
    """マスタデータをExcelからインポートする。

    model_class: インポート先SQLAlchemyモデルクラス（例: DepartmentMaster）
    fmt_key: excel_formats.yaml のキー（例: 'department'）
    """
    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        formats = _load_formats()
        ModelClass = model_class
        config_dict = formats[fmt_key]
        sheet_name = config_dict.get("sheet", 0)
        result = import_table(tmp_path, config_dict, ModelClass, sheet_name=sheet_name)

        if not result.data and not result.errors:
            return ImportResult(
                success=False,
                errors=[{"row": "-", "field": "-", "message": "データが見つかりませんでした。"}],
            )

        if result.errors:
            errors = [
                {"row": e.row, "field": e.column, "message": e.message}
                for e in result.errors
            ]
            return ImportResult(
                success=False,
                errors=errors,
                validation_error_count=len(errors),
            )

        for obj in result.data:
            db.session.merge(obj)
        db.session.commit()

        return ImportResult(success=True, saved_count=len(result.data))

    except Exception as exc:
        db.session.rollback()
        return ImportResult(
            success=False,
            errors=[{"row": "-", "field": "-", "message": str(exc)}],
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Master import helpers (used by maintenance.py two-step confirm flow)
# ---------------------------------------------------------------------------

def _read_and_validate_master(
    file_storage: FileStorage,
    fmt_key: str,
    current_count: int,
) -> MasterReadResult:
    """Excelからマスタ行を読み取り、バリデーションと件数警告を返す。"""
    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        formats = _load_formats()
        config_dict = formats[fmt_key]
        sheet_name = config_dict.get("sheet", 0)
        result = import_table(tmp_path, config_dict, dict, sheet_name=sheet_name)

        if result.errors:
            errors = [f"行 {e.row} [{e.column}]: {e.message}" for e in result.errors]
            return MasterReadResult(ok=False, errors=errors)

        if not result.data:
            return MasterReadResult(ok=False, errors=["データが見つかりませんでした。"])

        warnings: list[str] = []
        new_count = len(result.data)
        if current_count > 0 and new_count < current_count:
            warnings.append(
                f"現在 {current_count} 件のデータが {new_count} 件に置き換えられます。よろしいですか？"
            )

        return MasterReadResult(ok=True, rows=result.data, warnings=warnings)

    except Exception as exc:
        return MasterReadResult(ok=False, errors=[str(exc)])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def read_and_validate_section(file_storage: FileStorage, current_count: int) -> MasterReadResult:
    return _read_and_validate_master(file_storage, 'section', current_count)


def read_and_validate_department(file_storage: FileStorage, current_count: int) -> MasterReadResult:
    return _read_and_validate_master(file_storage, 'department', current_count)


def read_and_validate_district(file_storage: FileStorage, current_count: int) -> MasterReadResult:
    return _read_and_validate_master(file_storage, 'district', current_count)


def read_and_validate_kbn(file_storage: FileStorage, current_count: int) -> MasterReadResult:
    return _read_and_validate_master(file_storage, 'kbn', current_count)

def load_excel_format(fmt_key: str) -> ExcelConfig:
    """Excelフォーマット設定を読み込む。"""
    formats = _load_formats()
    if fmt_key not in formats:
        raise ValueError(f"不明なフォーマットキー: {fmt_key}")
    config_dict = formats[fmt_key]
    columns = [
        ColumnConfig(
            label=col["label"],
            field=col["field"],
            type=col.get("type", "str"),
            required=col.get("required", False),
            description=col.get("description"),
        )
        for col in config_dict["columns"]
    ]
    return ExcelConfig(
        columns=columns,
        header_row=config_dict.get("header_row", 1),
        sheet=config_dict.get("sheet"),
    )



# ---------------------------------------------------------------------------
# Pending (two-step confirm) helpers
# ---------------------------------------------------------------------------

def save_pending(rows: list[dict], kind: str) -> str:
    """行データを一時ファイルに保存し、トークンを返す。"""
    token = uuid.uuid4().hex
    path = Path(tempfile.gettempdir()) / f"mst_pending_{kind}_{token}.pkl"
    with open(path, "wb") as f:
        pickle.dump(rows, f)
    return token


def load_pending(token: str, kind: str) -> list[dict] | None:
    """トークンに対応する一時ファイルから行データを読み込む。"""
    path = Path(tempfile.gettempdir()) / f"mst_pending_{kind}_{token}.pkl"
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def delete_pending(token: str, kind: str) -> None:
    """トークンに対応する一時ファイルを削除する。"""
    path = Path(tempfile.gettempdir()) / f"mst_pending_{kind}_{token}.pkl"
    if path.exists():
        path.unlink()
