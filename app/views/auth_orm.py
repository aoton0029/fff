"""ORM-based auth views.

Comparison pattern against views/auth.py (db / raw-SQL pattern).

db パターン  → /auth/*         (auth_bp     in views/auth.py)
             uses authenticate_user from services/auth_service.py
                  → db_manager.fetch() → UserRecord (dataclass)

ORM パターン → /orm/auth/*     (auth_orm_bp in views/auth_orm.py)
             uses authenticate_user from services/auth_service_orm.py
                  → db.session.execute(select(User)) → User (ORM model)
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..forms.auth import LoginForm
from ..services.auth_service_orm import authenticate_user

auth_orm_bp = Blueprint("auth_orm", __name__, url_prefix="/orm/auth")


@auth_orm_bp.route("/login", methods=["GET", "POST"])
def login():
    """db パターンとの対比
    -------------------
    db  : authenticate_user() → UserRecord (dataclass / flask_login.UserMixin)
    ORM : authenticate_user() → User       (ORM model  / flask_login.UserMixin)
    どちらも login_user() に渡せる。
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.username.data, form.password.data)
        if user is None:
            flash("ユーザーIDまたはパスワードが正しくありません", "danger")
        else:
            login_user(user, remember=False)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

    return render_template("orm/auth/login.html", form=form)


@auth_orm_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_orm.login"))


@auth_orm_bp.route("/session-timeout")
def session_timeout():
    return render_template("orm/auth/session_timeout.html")
