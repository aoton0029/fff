"""Data importer service.

Orchestrates: read & validate via ExcelReader → save to DB → return result summary.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from ..extensions import db
from ..services.excel_reader import ExcelReader
from ..services.db_builders import get_builder
from ..models.dat_upload_batch import UploadBatch

_YAML_PATH = Path(__file__).parent.parent.parent / "config" / "excel_formats.yaml"


@dataclass
class ImportResult:
    success: bool
    saved_count: int = 0
    errors: list[dict] = field(default_factory=list)
    batch_id: int | None = None
    validation_error_count: int = 0


def import_excel_file(file_storage, file_type: str, user_id: int) -> ImportResult:
    """Process an uploaded FileStorage object.

    Saves to a temp file, reads & validates via ExcelReader, persists to DB,
    then deletes the temp file.
    """
    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        reader = ExcelReader(_YAML_PATH)
        result = reader.read(tmp_path, file_type)

        if not result.rows and not result.errors:
            return ImportResult(
                success=False,
                errors=[{"row": "-", "field": "-", "message": "データが見つかりませんでした。"}],
            )

        if result.errors:
            errors = [
                {"row": e.row_number, "field": "-", "message": e.error}
                for e in result.errors
            ]
            return ImportResult(
                success=False,
                errors=errors,
                validation_error_count=len(errors),
            )

        builder = get_builder(file_type)
        batch = UploadBatch(
            file_name=file_storage.filename,
            file_type=file_type,
            created_by=user_id,
        )
        db.session.add(batch)
        db.session.flush()

        records = [builder(m, batch.id, user_id) for m in result.rows]
        db.session.bulk_save_objects(records)
        batch.record_count = len(records)
        db.session.commit()

        return ImportResult(success=True, saved_count=len(records), batch_id=batch.id)

    except Exception as exc:
        db.session.rollback()
        return ImportResult(
            success=False,
            errors=[{"row": "-", "field": "-", "message": str(exc)}],
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
