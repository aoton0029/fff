from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class UploadForm(FlaskForm):
    file = FileField(
        'Excelファイル',
        validators=[
            FileRequired(message='ファイルを選択してください'),
            FileAllowed(['xlsx', 'xls'], message='Excelファイル(.xlsx / .xls)のみアップロードできます'),
        ],
    )
    submit = SubmitField('アップロード')
