from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from datetime import datetime

from app import db
from app.models import Teacher, Subject, SchoolClass, TeacherAttendance
from app.forms.teacher import TeacherForm
from app.utils.permissions import admin_required

teachers_bp = Blueprint("teachers", __name__, url_prefix="/teachers")


@teachers_bp.route("/")
@login_required
def index():
    if current_user.can_manage_users():
        teachers = Teacher.query.order_by(Teacher.employee_id).all()
        return render_template("teachers/list.html", teachers=teachers)
    if current_user.is_teacher and current_user.linked_id:
        teacher = Teacher.query.get(current_user.linked_id)
        if teacher:
            return redirect(url_for("teachers.detail", teacher_id=teacher.id))
    return render_template("teachers/index.html")


@teachers_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = TeacherForm()
    if form.validate_on_submit():
        if Teacher.query.filter_by(employee_id=form.employee_id.data).first():
            flash("Employee ID already exists.", "error")
            return render_template("teachers/form.html", form=form, title="New Teacher")
        teacher = Teacher(
            employee_id=form.employee_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data or None,
            phone=form.phone.data or None,
            join_date=form.join_date.data,
        )
        db.session.add(teacher)
        db.session.commit()
        flash("Teacher created.", "success")
        return redirect(url_for("teachers.index"))
    return render_template("teachers/form.html", form=form, title="New Teacher")


@teachers_bp.route("/<int:teacher_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(obj=teacher)
    if form.validate_on_submit():
        other = Teacher.query.filter(
            Teacher.employee_id == form.employee_id.data,
            Teacher.id != teacher_id,
        ).first()
        if other:
            flash("Employee ID already exists.", "error")
            return render_template("teachers/form.html", form=form, teacher=teacher, title="Edit Teacher")
        teacher.employee_id = form.employee_id.data
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data or None
        teacher.phone = form.phone.data or None
        teacher.join_date = form.join_date.data
        db.session.commit()
        flash("Teacher updated.", "success")
        return redirect(url_for("teachers.index"))
    return render_template("teachers/form.html", form=form, teacher=teacher, title="Edit Teacher")


@teachers_bp.route("/<int:teacher_id>")
@login_required
def detail(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if current_user.is_teacher and current_user.linked_id != teacher_id:
        from flask import abort
        abort(403)
    subjects = teacher.subjects.all()
    return render_template("teachers/detail.html", teacher=teacher, subjects=subjects)


@teachers_bp.route("/attendance", methods=["GET", "POST"])
@login_required
@admin_required
def mark_attendance():
    if request.method == "POST":
        att_date_str = request.form.get("date")
        if not att_date_str:
            flash("Date is required.", "error")
        else:
            try:
                att_date = datetime.strptime(att_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                flash("Invalid date.", "error")
            else:
                teachers = Teacher.query.order_by(Teacher.employee_id).all()
                for t in teachers:
                    key = f"status_{t.id}"
                    status = request.form.get(key)
                    if status in ("present", "absent", "late"):
                        rec = TeacherAttendance.query.filter_by(teacher_id=t.id, date=att_date).first()
                        if rec:
                            rec.status = status
                            rec.remarks = request.form.get(f"remarks_{t.id}") or None
                        else:
                            rec = TeacherAttendance(
                                teacher_id=t.id,
                                date=att_date,
                                status=status,
                                remarks=request.form.get(f"remarks_{t.id}") or None,
                            )
                            db.session.add(rec)
                db.session.commit()
                flash("Attendance saved.", "success")
                return redirect(url_for("teachers.mark_attendance"))
    att_date = request.args.get("date")
    teachers = Teacher.query.order_by(Teacher.employee_id).all()
    existing = {}
    if att_date:
        try:
            d = datetime.strptime(att_date, "%Y-%m-%d").date()
            recs = TeacherAttendance.query.filter_by(date=d).all()
            existing = {r.teacher_id: r for r in recs}
        except (ValueError, TypeError):
            pass
    for t in teachers:
        t._attendance = existing.get(t.id)
    return render_template("teachers/mark_attendance.html", teachers=teachers, att_date=att_date)


@teachers_bp.route("/<int:teacher_id>/attendance")
@login_required
def attendance_list(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if current_user.is_teacher and current_user.linked_id != teacher_id:
        from flask import abort
        abort(403)
    records = TeacherAttendance.query.filter_by(teacher_id=teacher_id).order_by(
        TeacherAttendance.date.desc()
    ).limit(100).all()
    return render_template("teachers/attendance_list.html", teacher=teacher, records=records)


@teachers_bp.route("/<int:teacher_id>/subjects", methods=["GET", "POST"])
@login_required
@admin_required
def edit_subjects(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if request.method == "POST":
        subject_ids = request.form.getlist("subject_ids", type=int)
        teacher.subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        db.session.commit()
        flash("Subjects updated.", "success")
        return redirect(url_for("teachers.detail", teacher_id=teacher_id))
    all_subjects = Subject.query.order_by(Subject.name).all()
    selected_ids = [s.id for s in teacher.subjects.all()]
    return render_template(
        "teachers/edit_subjects.html",
        teacher=teacher,
        all_subjects=all_subjects,
        selected_ids=selected_ids,
    )
