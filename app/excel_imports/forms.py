from flask_wtf import FlaskForm
from wtforms import SubmitField


class ExcelImportForm(FlaskForm):
    submit = SubmitField("取込")
