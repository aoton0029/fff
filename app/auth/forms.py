from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "ユーザーID",
        validators=[DataRequired(message="ユーザーIDを入力してください"), Length(max=255)],
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(message="パスワードを入力してください")],
    )
    submit = SubmitField("ログイン")
