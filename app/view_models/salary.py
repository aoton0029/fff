from dataclasses import dataclass, field
from sqlalchemy import select

from ..extensions import db
from ..forms.upload import UploadForm
from ..models.dat_upload_batch import UploadBatch

_FILE_TYPE = 'salary'


@dataclass
class SalaryIndexViewModel:
    form: UploadForm = field(init=False)
    batch: object = field(init=False)
    file_type: str = field(init=False, default=_FILE_TYPE)

    def __post_init__(self):
        self.form = UploadForm()
        self.file_type = _FILE_TYPE
        self.batch = db.session.scalar(
            select(UploadBatch)
            .filter_by(file_type=_FILE_TYPE)
            .order_by(UploadBatch.created_at.desc())
        )
