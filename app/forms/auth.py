# Deprecated: use app.auth.forms
from ..auth.forms import LoginForm  # noqa: F401

__all__ = ["LoginForm"]
    username = StringField(
        "ユーザーID",
        validators=[DataRequired(message="ユーザーIDを入力してください"), Length(max=255)],
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(message="パスワードを入力してください")],
    )
    submit = SubmitField("ログイン")
