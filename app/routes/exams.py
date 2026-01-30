from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from decimal import Decimal

from app import db
from app.models import Exam, ExamResult, Student, SchoolClass, Subject
from app.forms.exam import ExamForm
from app.utils.permissions import admin_required

exams_bp = Blueprint("exams", __name__, url_prefix="/exams")


@exams_bp.route("/")
@login_required
@admin_required
def index():
    exams = Exam.query.order_by(Exam.exam_date.desc(), Exam.name).all()
    return render_template("exams/list.html", exams=exams)


@exams_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = ExamForm()
    form.class_id.choices = [(c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()]
    form.subject_id.choices = [(s.id, str(s)) for s in Subject.query.order_by(Subject.name).all()]
    if form.validate_on_submit():
        exam = Exam(
            name=form.name.data,
            exam_type=form.exam_type.data,
            class_id=form.class_id.data,
            subject_id=form.subject_id.data,
            max_marks=form.max_marks.data or 100,
            exam_date=form.exam_date.data,
        )
        db.session.add(exam)
        db.session.commit()
        flash("Exam created.", "success")
        return redirect(url_for("exams.index"))
    return render_template("exams/form.html", form=form, title="New Exam")


@exams_bp.route("/<int:exam_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    form = ExamForm(obj=exam)
    form.class_id.choices = [(c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()]
    form.subject_id.choices = [(s.id, str(s)) for s in Subject.query.order_by(Subject.name).all()]
    if form.validate_on_submit():
        exam.name = form.name.data
        exam.exam_type = form.exam_type.data
        exam.class_id = form.class_id.data
        exam.subject_id = form.subject_id.data
        exam.max_marks = form.max_marks.data or 100
        exam.exam_date = form.exam_date.data
        db.session.commit()
        flash("Exam updated.", "success")
        return redirect(url_for("exams.index"))
    form.class_id.data = exam.class_id
    form.subject_id.data = exam.subject_id
    return render_template("exams/form.html", form=form, exam=exam, title="Edit Exam")


@exams_bp.route("/<int:exam_id>")
@login_required
@admin_required
def detail(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    results = ExamResult.query.filter_by(exam_id=exam_id).all()
    return render_template("exams/detail.html", exam=exam, results=results)


@exams_bp.route("/<int:exam_id>/results", methods=["GET", "POST"])
@login_required
@admin_required
def enter_results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    students = Student.query.filter_by(class_id=exam.class_id).order_by(Student.admission_no).all()
    if request.method == "POST":
        for s in students:
            marks_str = request.form.get(f"marks_{s.id}")
            grade = request.form.get(f"grade_{s.id}") or None
            remarks = request.form.get(f"remarks_{s.id}") or None
            marks = None
            if marks_str is not None and marks_str.strip() != "":
                try:
                    marks = Decimal(marks_str)
                except Exception:
                    pass
            rec = ExamResult.query.filter_by(exam_id=exam_id, student_id=s.id).first()
            if rec:
                rec.marks_obtained = marks
                rec.grade = grade
                rec.remarks = remarks
            else:
                rec = ExamResult(exam_id=exam_id, student_id=s.id, marks_obtained=marks, grade=grade, remarks=remarks)
                db.session.add(rec)
        db.session.commit()
        flash("Results saved.", "success")
        return redirect(url_for("exams.detail", exam_id=exam_id))
    existing = {r.student_id: r for r in ExamResult.query.filter_by(exam_id=exam_id).all()}
    for s in students:
        s._result = existing.get(s.id)
    return render_template("exams/enter_results.html", exam=exam, students=students)
