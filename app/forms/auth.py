from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        'ユーザー名',
        validators=[DataRequired(message='ユーザー名を入力してください'), Length(max=150)],
    )
    password = PasswordField(
        'パスワード',
        validators=[DataRequired(message='パスワードを入力してください')],
    )
    submit = SubmitField('ログイン')
