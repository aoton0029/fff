from dataclasses import dataclass, field
from sqlalchemy import func, select

from ..extensions import db
from ..forms.upload import UploadForm
from ..models.dat_salary import SalaryData
from ..models.dat_upload_batch import UploadBatch

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
        query = select(UploadBatch).filter_by(file_type=_FILE_TYPE).order_by(UploadBatch.created_at.desc())
        self.pagination = db.paginate(query, page=self.page, per_page=_PER_PAGE, error_out=False)
        self.batches = self.pagination.items
        self.salary_count = db.session.scalar(select(func.count()).select_from(SalaryData))
