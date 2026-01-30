from datetime import datetime
from io import StringIO
import csv

from flask import Blueprint, render_template, request, Response
from flask_login import login_required

from app.models import Student, SchoolClass, Exam
from app.services.reports import attendance_report_students, exam_performance_report, fees_collected_report
from app.utils.permissions import admin_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
@admin_required
def index():
    return render_template("reports/index.html")


@reports_bp.route("/attendance", methods=["GET", "POST"])
@login_required
@admin_required
def attendance():
    student_id = request.args.get("student_id", type=int) or request.form.get("student_id", type=int)
    class_id = request.args.get("class_id", type=int) or request.form.get("class_id", type=int)
    start = request.args.get("start") or request.form.get("start")
    end = request.args.get("end") or request.form.get("end")
    group_by = request.args.get("group_by") or request.form.get("group_by") or "month"
    start_date = datetime.strptime(start, "%Y-%m-%d").date() if start else None
    end_date = datetime.strptime(end, "%Y-%m-%d").date() if end else None
    rows = []
    if start_date and end_date:
        rows = attendance_report_students(student_id=student_id, class_id=class_id, start_date=start_date, end_date=end_date, group_by=group_by)
    students = Student.query.order_by(Student.admission_no).all()
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    if request.args.get("export") == "csv" and rows:
        return _csv_response(
            ["Period", "Total Days", "Present", "Absent", "Late", "Percentage"],
            [[r["period"], r["total"], r["present"], r["absent"], r["late"], r["percentage"]] for r in rows],
            "attendance_report.csv",
        )
    return render_template("reports/attendance.html", rows=rows, students=students, classes=classes, student_id=student_id, class_id=class_id, start=start, end=end, group_by=group_by)


@reports_bp.route("/exam-performance", methods=["GET", "POST"])
@login_required
@admin_required
def exam_performance():
    student_id = request.args.get("student_id", type=int) or request.form.get("student_id", type=int)
    class_id = request.args.get("class_id", type=int) or request.form.get("class_id", type=int)
    exam_id = request.args.get("exam_id", type=int) or request.form.get("exam_id", type=int)
    rows = exam_performance_report(student_id=student_id, class_id=class_id, exam_id=exam_id)
    students = Student.query.order_by(Student.admission_no).all()
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    exams = Exam.query.order_by(Exam.exam_date.desc()).limit(100).all()
    if request.args.get("export") == "csv" and rows:
        headers = ["Student", "Exam", "Subject", "Marks", "Grade"]
        data = [[r["student"], r["exam"], r.get("subject", ""), r.get("marks"), r.get("grade")] for r in rows]
        return _csv_response(headers, data, "exam_performance_report.csv")
    return render_template("reports/exam_performance.html", rows=rows, students=students, classes=classes, exams=exams, student_id=student_id, class_id=class_id, exam_id=exam_id)


@reports_bp.route("/fees-collected", methods=["GET", "POST"])
@login_required
@admin_required
def fees_collected():
    academic_year = request.args.get("academic_year") or request.form.get("academic_year")
    term = request.args.get("term") or request.form.get("term")
    class_id = request.args.get("class_id", type=int) or request.form.get("class_id", type=int)
    rows = []
    total_collected = 0
    if academic_year:
        rows, total_collected = fees_collected_report(academic_year=academic_year, term=term or None, class_id=class_id)
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    if request.args.get("export") == "csv" and rows:
        return _csv_response(
            ["Class", "Collected", "Expected"],
            [[r["class"], r["collected"], r["expected"]] for r in rows],
            "fees_collected_report.csv",
        )
    return render_template("reports/fees_collected.html", rows=rows, total_collected=total_collected, classes=classes, academic_year=academic_year, term=term, class_id=class_id)


def _csv_response(headers, rows, filename):
    si = StringIO()
    w = csv.writer(si)
    w.writerow(headers)
    w.writerows(rows)
    output = si.getvalue()
    si.close()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
