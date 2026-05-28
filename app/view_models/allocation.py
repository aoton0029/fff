from dataclasses import dataclass, field

from ..forms.upload import UploadForm
from ..models.upload_batch import UploadBatch

_PER_PAGE = 20
_FILE_TYPE = 'allocation'


@dataclass
class AllocationIndexViewModel:
    page: int
    form: UploadForm = field(init=False)
    pagination: object = field(init=False)
    batches: list = field(init=False)
    file_type: str = field(init=False, default=_FILE_TYPE)

    def __post_init__(self):
        self.form = UploadForm()
        self.file_type = _FILE_TYPE
        query = (
            UploadBatch.query
            .filter_by(file_type=_FILE_TYPE)
            .order_by(UploadBatch.created_at.desc())
        )
        self.pagination = query.paginate(page=self.page, per_page=_PER_PAGE, error_out=False)
        self.batches = self.pagination.items
