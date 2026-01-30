from datetime import datetime, date, timedelta
from collections import defaultdict

from app.models import (
    StudentAttendance,
    ExamResult,
    FeePayment,
    FeeStructure,
    Student,
    SchoolClass,
    Exam,
)


def attendance_report_students(student_id=None, class_id=None, start_date=None, end_date=None, group_by="month"):
    q = StudentAttendance.query
    if student_id:
        q = q.filter_by(student_id=student_id)
    if start_date:
        q = q.filter(StudentAttendance.date >= start_date)
    if end_date:
        q = q.filter(StudentAttendance.date <= end_date)
    if class_id:
        q = q.join(StudentAttendance.student).filter(Student.class_id == class_id)
    records = q.all()
    # Group by week/month/year
    groups = defaultdict(lambda: {"present": 0, "absent": 0, "late": 0, "total": 0})
    for r in records:
        d = r.date
        if group_by == "week":
            key = d - timedelta(days=d.weekday())
        elif group_by == "year":
            key = date(d.year, 1, 1)
        else:
            key = date(d.year, d.month, 1)
        groups[key]["total"] += 1
        groups[key][r.status] = groups[key].get(r.status, 0) + 1
    rows = []
    for k in sorted(groups.keys(), reverse=True):
        g = groups[k]
        pct = (g["present"] / g["total"] * 100) if g["total"] else 0
        rows.append({
            "period": k.strftime("%Y-%m" if group_by == "month" else "%Y-%m-%d" if group_by == "week" else "%Y"),
            "total": g["total"],
            "present": g["present"],
            "absent": g["absent"],
            "late": g["late"],
            "percentage": round(pct, 1),
        })
    return rows


def exam_performance_report(student_id=None, class_id=None, exam_id=None):
    if exam_id:
        results = ExamResult.query.filter_by(exam_id=exam_id).all()
        return [{"student": r.student.full_name, "exam": r.exam.name, "marks": r.marks_obtained, "grade": r.grade} for r in results]
    q = ExamResult.query
    if student_id:
        q = q.filter_by(student_id=student_id)
    if class_id:
        q = q.join(ExamResult.student).filter(Student.class_id == class_id)
    results = q.join(ExamResult.exam).order_by(Exam.id.desc()).limit(500).all()
    return [
        {"student": r.student.full_name, "exam": r.exam.name, "subject": r.exam.subject.name if r.exam.subject else "", "marks": r.marks_obtained, "grade": r.grade}
        for r in results
    ]


def fees_collected_report(academic_year=None, term=None, class_id=None):
    q = FeePayment.query
    if academic_year:
        q = q.join(FeePayment.fee_structure).filter(FeeStructure.academic_year == academic_year)
    if term:
        q = q.join(FeePayment.fee_structure).filter(FeeStructure.term == term)
    if class_id:
        q = q.join(FeePayment.fee_structure).filter(FeeStructure.class_id == class_id)
    payments = q.all()
    by_class = defaultdict(lambda: {"collected": 0, "expected": 0})
    total_collected = sum(p.amount_paid for p in payments)
    for p in payments:
        fs = p.fee_structure
        key = fs.school_class.name if fs.school_class else "Unknown"
        by_class[key]["collected"] += float(p.amount_paid)
    structures = FeeStructure.query
    if academic_year:
        structures = structures.filter_by(academic_year=academic_year)
    if term:
        structures = structures.filter(FeeStructure.term == term)
    if class_id:
        structures = structures.filter_by(class_id=class_id)
    for fs in structures.all():
        key = fs.school_class.name if fs.school_class else "Unknown"
        by_class[key]["expected"] += float(fs.amount) * Student.query.filter_by(class_id=fs.class_id).count()
    rows = [{"class": k, "collected": v["collected"], "expected": v["expected"]} for k, v in sorted(by_class.items())]
    return rows, total_collected
