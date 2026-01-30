from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.forms.auth import LoginForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def get_redirect_after_login():
    if not current_user.is_authenticated:
        return url_for("main.index")
    if current_user.is_super_admin or current_user.is_head_teacher:
        return url_for("admin.dashboard")
    if current_user.is_teacher:
        return url_for("teachers.index")
    if current_user.is_student:
        return url_for("students.index")
    return url_for("main.index")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(get_redirect_after_login())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html", form=form)
        if not user.is_active:
            flash("Account is deactivated.", "error")
            return render_template("auth/login.html", form=form)
        login_user(user, remember=form.remember.data)
        next_page = request.args.get("next") or get_redirect_after_login()
        return redirect(next_page)
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
