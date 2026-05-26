from flask_wtf import FlaskForm
from wtforms import SubmitField


class FileUploadForm(FlaskForm):
    """CSRF-protected form for file uploads. Files are handled via request.files."""

    submit = SubmitField("アップロード")
