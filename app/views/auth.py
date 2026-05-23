from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms.auth import LoginForm
from ..services.auth_service import authenticate_user

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
