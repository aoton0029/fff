from .salary import SalaryRow
from .allocation import AllocationRow
from .labor_transfer import LaborTransferRow
from .ouen import OuenRow
from pydantic import BaseModel

_registry: dict[str, type[BaseModel]] = {}


def register(file_type: str, model: type[BaseModel]) -> None:
    _registry[file_type] = model


def get_model(file_type: str) -> type[BaseModel]:
    try:
        return _registry[file_type]
    except KeyError:
        available = ", ".join(_registry)
        raise KeyError(
            f"file_type '{file_type}' は未登録です。利用可能: {available}"
        ) from None

def registered_types() -> list[str]:
    return list(_registry.keys())

register("salary", SalaryRow)
register("allocation", AllocationRow)
register("labor_transfer", LaborTransferRow)
register("ouen", OuenRow)


__all__ = ['SalaryRow', 'AllocationRow', 'LaborTransferRow', 'OuenRow', 'get_model', 'registered_types']
