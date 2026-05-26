from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm
from .service import authenticate_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/session-timeout")
def session_timeout():
    return render_template("auth/session_timeout.html")
