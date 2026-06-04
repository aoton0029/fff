from dataclasses import dataclass, field

from ..forms.upload import UploadForm
from ..repositories.batch_repository import UploadBatchRepository

_PER_PAGE = 20
_FILE_TYPE = 'labor_transfer'

_batch_repo = UploadBatchRepository()


@dataclass
class LaborIndexViewModel:
    page: int
    sort_by: str = 'created_at'
    sort_dir: str = 'desc'
    form: UploadForm = field(init=False)
    pagination: object = field(init=False)
    batches: list = field(init=False)
    file_type: str = field(init=False, default=_FILE_TYPE)

    def __post_init__(self):
        self.form = UploadForm()
        self.file_type = _FILE_TYPE
        self.pagination = _batch_repo.get_paginated(_FILE_TYPE, self.page, _PER_PAGE, self.sort_by, self.sort_dir)
        self.batches = self.pagination.items
