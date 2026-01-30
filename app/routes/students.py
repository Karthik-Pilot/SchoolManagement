from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from datetime import datetime, date as date_type

from app import db
from app.models import Student, SchoolClass, StudentAttendance, ExamResult, ConductCertificate
from app.forms.student import StudentForm
from app.forms.attendance import BulkAttendanceForm
from app.forms.conduct import ConductCertificateForm
from app.utils.permissions import admin_required

students_bp = Blueprint("students", __name__, url_prefix="/students")


def _student_list_query():
    q = Student.query
    class_id = request.args.get("class_id", type=int)
    section = request.args.get("section")
    if class_id:
        q = q.filter_by(class_id=class_id)
    if section:
        q = q.filter_by(section=section)
    return q.order_by(Student.admission_no)


@students_bp.route("/")
@login_required
def index():
    if current_user.can_manage_users() or current_user.is_teacher:
        students = _student_list_query().all()
        classes = SchoolClass.query.order_by(SchoolClass.name).all()
        return render_template(
            "students/list.html",
            students=students,
            classes=classes,
            class_filter=request.args.get("class_id", type=int),
            section_filter=request.args.get("section"),
        )
    # Student: show only self
    if current_user.is_student and current_user.linked_id:
        student = Student.query.get(current_user.linked_id)
        if student:
            return render_template("students/detail.html", student=student)
    return render_template("students/index.html")


@students_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = StudentForm()
    form.class_id.choices = [("", "")] + [
        (c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()
    ]
    if form.validate_on_submit():
        if Student.query.filter_by(admission_no=form.admission_no.data).first():
            flash("Admission number already exists.", "error")
            return render_template("students/form.html", form=form, title="New Student")
        student = Student(
            admission_no=form.admission_no.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            gender=form.gender.data or None,
            class_id=form.class_id.data or None,
            section=form.section.data or None,
            guardian_name=form.guardian_name.data or None,
            guardian_contact=form.guardian_contact.data or None,
            address=form.address.data or None,
            admission_date=form.admission_date.data,
        )
        db.session.add(student)
        db.session.commit()
        flash("Student created.", "success")
        return redirect(url_for("students.index"))
    return render_template("students/form.html", form=form, title="New Student")


@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    form.class_id.choices = [("", "")] + [
        (c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()
    ]
    if form.validate_on_submit():
        other = Student.query.filter(
            Student.admission_no == form.admission_no.data,
            Student.id != student_id,
        ).first()
        if other:
            flash("Admission number already exists.", "error")
            return render_template("students/form.html", form=form, student=student, title="Edit Student")
        student.admission_no = form.admission_no.data
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.dob = form.dob.data
        student.gender = form.gender.data or None
        student.class_id = form.class_id.data or None
        student.section = form.section.data or None
        student.guardian_name = form.guardian_name.data or None
        student.guardian_contact = form.guardian_contact.data or None
        student.address = form.address.data or None
        student.admission_date = form.admission_date.data
        db.session.commit()
        flash("Student updated.", "success")
        return redirect(url_for("students.index"))
    form.class_id.data = student.class_id
    return render_template("students/form.html", form=form, student=student, title="Edit Student")


@students_bp.route("/attendance", methods=["GET", "POST"])
@login_required
@admin_required
def mark_attendance():
    form = BulkAttendanceForm()
    form.class_id.choices = [("", "")] + [
        (c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()
    ]
    if request.method == "POST":
        att_date_str = request.form.get("date")
        class_id = request.form.get("class_id", type=int)
        section = request.form.get("section") or None
        if not att_date_str or not class_id:
            flash("Date and class are required.", "error")
        else:
            try:
                att_date = datetime.strptime(att_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                att_date = None
            if not att_date:
                flash("Invalid date.", "error")
            else:
                students = Student.query.filter(Student.class_id == class_id)
                if section:
                    students = students.filter(Student.section == section)
                students = students.order_by(Student.admission_no).all()
                for s in students:
                    key = f"status_{s.id}"
                    status = request.form.get(key)
                    if status in ("present", "absent", "late"):
                        rec = StudentAttendance.query.filter_by(
                            student_id=s.id, date=att_date
                        ).first()
                        if rec:
                            rec.status = status
                            rec.remarks = request.form.get(f"remarks_{s.id}") or None
                        else:
                            rec = StudentAttendance(
                                student_id=s.id,
                                date=att_date,
                                status=status,
                                remarks=request.form.get(f"remarks_{s.id}") or None,
                            )
                            db.session.add(rec)
                db.session.commit()
                flash("Attendance saved.", "success")
                return redirect(url_for("students.mark_attendance"))
    # GET: show form or list for date+class
    att_date = request.args.get("date")
    class_id = request.args.get("class_id", type=int)
    section = request.args.get("section")
    students = []
    if att_date and class_id:
        try:
            d = datetime.strptime(att_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            d = None
        if d:
            students = Student.query.filter(Student.class_id == class_id)
            if section:
                students = students.filter(Student.section == section)
            students = students.order_by(Student.admission_no).all()
            # Load existing attendance for this date
            existing = {
                a.student_id: a
                for a in StudentAttendance.query.filter(
                    StudentAttendance.date == d,
                    StudentAttendance.student_id.in_([s.id for s in students]),
                ).all()
            }
            for s in students:
                s._attendance = existing.get(s.id)
    return render_template(
        "students/mark_attendance.html",
        form=form,
        students=students,
        att_date=att_date,
        class_id=class_id,
        section=section,
    )


@students_bp.route("/<int:student_id>/attendance")
@login_required
def attendance_list(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.is_student and current_user.linked_id != student_id:
        from flask import abort
        abort(403)
    records = StudentAttendance.query.filter_by(student_id=student_id).order_by(
        StudentAttendance.date.desc()
    ).limit(100).all()
    return render_template("students/attendance_list.html", student=student, records=records)


@students_bp.route("/<int:student_id>/performance")
@login_required
def performance(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.is_student and current_user.linked_id != student_id:
        from flask import abort
        abort(403)
    records = (
        ExamResult.query.join(ExamResult.exam)
        .filter(ExamResult.student_id == student_id)
        .order_by(ExamResult.exam_id.desc())
        .all()
    )
    from decimal import Decimal
    total_marks = sum((r.marks_obtained or 0) for r in records)
    count = len([r for r in records if r.marks_obtained is not None])
    average = (total_marks / count) if count else None
    return render_template(
        "students/performance.html",
        student=student,
        records=records,
        average=average,
        count=count,
    )


@students_bp.route("/<int:student_id>/conduct")
@login_required
def conduct_list(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.is_student and current_user.linked_id != student_id:
        from flask import abort
        abort(403)
    records = ConductCertificate.query.filter_by(student_id=student_id).order_by(
        ConductCertificate.issue_date.desc()
    ).all()
    return render_template("students/conduct_list.html", student=student, records=records)


@students_bp.route("/<int:student_id>/conduct/new", methods=["GET", "POST"])
@login_required
@admin_required
def conduct_create(student_id):
    student = Student.query.get_or_404(student_id)
    form = ConductCertificateForm()
    if form.validate_on_submit():
        rec = ConductCertificate(
            student_id=student_id,
            type=form.type.data,
            title=form.title.data,
            description=form.description.data or None,
            issue_date=form.issue_date.data,
        )
        db.session.add(rec)
        db.session.commit()
        flash("Record added.", "success")
        return redirect(url_for("students.conduct_list", student_id=student_id))
    return render_template("students/conduct_form.html", form=form, student=student, title="Add Conduct/Certificate")


@students_bp.route("/<int:student_id>/conduct/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def conduct_edit(student_id, record_id):
    student = Student.query.get_or_404(student_id)
    rec = ConductCertificate.query.filter_by(id=record_id, student_id=student_id).first_or_404()
    form = ConductCertificateForm(obj=rec)
    if form.validate_on_submit():
        rec.type = form.type.data
        rec.title = form.title.data
        rec.description = form.description.data or None
        rec.issue_date = form.issue_date.data
        db.session.commit()
        flash("Record updated.", "success")
        return redirect(url_for("students.conduct_list", student_id=student_id))
    return render_template("students/conduct_form.html", form=form, student=student, record=rec, title="Edit Conduct/Certificate")


@students_bp.route("/<int:student_id>")
@login_required
def detail(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.is_student and current_user.linked_id != student_id:
        from flask import abort
        abort(403)
    if current_user.is_teacher and not current_user.can_manage_users():
        # TODO: check if teacher teaches this student's class
        pass
    return render_template("students/detail.html", student=student)
