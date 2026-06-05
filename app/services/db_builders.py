"""DB record builder registry.

Each builder converts a validated Pydantic row model into a SQLAlchemy DB record.
Row models expose to_db_kwargs() for the field mapping; builders only handle
DB model instantiation and common fields.

To add a new file_type: define a builder function and call register().
"""
from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel

from ..models.dat_salary import SalaryData
from ..models.dat_allocation import AllocationData
from ..models.dat_labor_transfer import LaborTransferData
from ..models.dat_ouen import OuenData
from ..models.mst_section import SectionMaster

BuilderFn = Callable[[BaseModel, int, int], Any]

_registry: dict[str, BuilderFn] = {}


def register(file_type: str, fn: BuilderFn) -> None:
    _registry[file_type] = fn


def get_builder(file_type: str) -> BuilderFn:
    try:
        return _registry[file_type]
    except KeyError:
        available = ", ".join(_registry)
        raise KeyError(
            f"file_type '{file_type}' は未登録です。利用可能: {available}"
        ) from None


def _build_salary(model: BaseModel, batch_id: int, user_id: int) -> SalaryData:
    return SalaryData(**model.to_db_kwargs(), batch_id=batch_id, created_by=user_id)


def _build_allocation(model: BaseModel, batch_id: int, user_id: int) -> AllocationData:
    return AllocationData(**model.to_db_kwargs(), batch_id=batch_id, created_by=user_id)


def _build_labor_transfer(model: BaseModel, batch_id: int, user_id: int) -> LaborTransferData:
    return LaborTransferData(**model.to_db_kwargs(), batch_id=batch_id, created_by=user_id)


def _build_ouen(model: BaseModel, batch_id: int, user_id: int) -> OuenData:
    kwargs = model.to_db_kwargs()
    from_section = SectionMaster.query.get(kwargs["from_section_code"])
    to_section = SectionMaster.query.get(kwargs["to_section_code"])
    if from_section is None:
        raise ValueError(f"送り出し課コードが存在しません: {kwargs['from_section_code']}")
    if to_section is None:
        raise ValueError(f"受け入れ課コードが存在しません: {kwargs['to_section_code']}")
    return OuenData(
        **kwargs,
        from_district=from_section.district_code,
        to_district=to_section.district_code,
        batch_id=batch_id,
        created_by=user_id,
    )


register("salary", _build_salary)
register("allocation", _build_allocation)
register("labor_transfer", _build_labor_transfer)
register("ouen", _build_ouen)
