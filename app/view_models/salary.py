from dataclasses import dataclass, field

from ..forms.upload import UploadForm
from ..repositories.batch_repository import UploadBatchRepository

_FILE_TYPE = 'salary'

_batch_repo = UploadBatchRepository()


@dataclass
class SalaryIndexViewModel:
    form: UploadForm = field(init=False)
    batch: object = field(init=False)
    file_type: str = field(init=False, default=_FILE_TYPE)

    def __post_init__(self):
        self.form = UploadForm()
        self.file_type = _FILE_TYPE
        self.batch = _batch_repo.get_latest(_FILE_TYPE)
