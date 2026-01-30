from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import User, SchoolClass, Subject
from app.forms.user import UserForm
from app.forms.school_class import SchoolClassForm
from app.forms.subject import SubjectForm
from app.utils.permissions import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/users")
@login_required
@admin_required
def user_list():
    role_filter = request.args.get("role")
    q = User.query
    if role_filter:
        q = q.filter_by(role=role_filter)
    users = q.order_by(User.username).all()
    return render_template("admin/user_list.html", users=users, role_filter=role_filter)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "error")
            return render_template("admin/user_form.html", form=form, title="New User")
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists.", "error")
            return render_template("admin/user_form.html", form=form, title="New User")
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            linked_id=form.linked_id.data or None,
        )
        user.set_password(form.password.data or "changeme")
        db.session.add(user)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.user_list"))
    return render_template("admin/user_form.html", form=form, title="New User")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role.choices = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("head_teacher", "Head Teacher"),
        ("super_admin", "Super Admin"),
    ]
    if form.validate_on_submit():
        other = User.query.filter(
            User.username == form.username.data,
            User.id != user_id,
        ).first()
        if other:
            flash("Username already exists.", "error")
            return render_template("admin/user_form.html", form=form, user=user, title="Edit User")
        other_email = User.query.filter(
            User.email == form.email.data,
            User.id != user_id,
        ).first()
        if other_email:
            flash("Email already exists.", "error")
            return render_template("admin/user_form.html", form=form, user=user, title="Edit User")
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.linked_id = form.linked_id.data or None
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.user_list"))
    form.linked_id.data = user.linked_id
    return render_template("admin/user_form.html", form=form, user=user, title="Edit User")


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@login_required
@admin_required
def user_deactivate(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate yourself.", "error")
        return redirect(url_for("admin.user_list"))
    user.is_active = False
    db.session.commit()
    flash("User deactivated.", "success")
    return redirect(url_for("admin.user_list"))


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@login_required
@admin_required
def user_activate(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash("User activated.", "success")
    return redirect(url_for("admin.user_list"))


# Classes
@admin_bp.route("/classes")
@login_required
@admin_required
def class_list():
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    return render_template("admin/class_list.html", classes=classes)


@admin_bp.route("/classes/new", methods=["GET", "POST"])
@login_required
@admin_required
def class_create():
    form = SchoolClassForm()
    if form.validate_on_submit():
        c = SchoolClass(name=form.name.data, academic_year=form.academic_year.data)
        db.session.add(c)
        db.session.commit()
        flash("Class created.", "success")
        return redirect(url_for("admin.class_list"))
    return render_template("admin/class_form.html", form=form, title="New Class")


@admin_bp.route("/classes/<int:class_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def class_edit(class_id):
    c = SchoolClass.query.get_or_404(class_id)
    form = SchoolClassForm(obj=c)
    if form.validate_on_submit():
        c.name = form.name.data
        c.academic_year = form.academic_year.data
        db.session.commit()
        flash("Class updated.", "success")
        return redirect(url_for("admin.class_list"))
    return render_template("admin/class_form.html", form=form, class_obj=c, title="Edit Class")


# Subjects
@admin_bp.route("/subjects")
@login_required
@admin_required
def subject_list():
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template("admin/subject_list.html", subjects=subjects)


@admin_bp.route("/subjects/new", methods=["GET", "POST"])
@login_required
@admin_required
def subject_create():
    form = SubjectForm()
    if form.validate_on_submit():
        s = Subject(name=form.name.data, code=form.code.data or None)
        db.session.add(s)
        db.session.commit()
        flash("Subject created.", "success")
        return redirect(url_for("admin.subject_list"))
    return render_template("admin/subject_form.html", form=form, title="New Subject")


@admin_bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def subject_edit(subject_id):
    s = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=s)
    if form.validate_on_submit():
        s.name = form.name.data
        s.code = form.code.data or None
        db.session.commit()
        flash("Subject updated.", "success")
        return redirect(url_for("admin.subject_list"))
    return render_template("admin/subject_form.html", form=form, subject=s, title="Edit Subject")
