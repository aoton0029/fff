from dataclasses import dataclass, field

from ..forms.upload import UploadForm
from ..models.salary import SalaryData
from ..models.upload_batch import UploadBatch

_PER_PAGE = 20
_FILE_TYPE = 'ouen'


@dataclass
class OuenIndexViewModel:
    page: int
    form: UploadForm = field(init=False)
    pagination: object = field(init=False)
    batches: list = field(init=False)
    salary_count: int = field(init=False)

    def __post_init__(self):
        self.form = UploadForm()
        query = UploadBatch.query.filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
        self.pagination = query.paginate(page=self.page, per_page=_PER_PAGE, error_out=False)
        self.batches = self.pagination.items
        self.salary_count = SalaryData.query.count()
