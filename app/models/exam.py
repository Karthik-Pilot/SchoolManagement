from datetime import date

from app import db


class Exam(db.Model):
    __tablename__ = "exam"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    exam_type = db.Column(db.String(20), nullable=False, default="exam")  # exam, test
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False, index=True)
    max_marks = db.Column(db.Numeric(10, 2), nullable=False, default=100)
    exam_date = db.Column(db.Date, nullable=True)

    school_class = db.relationship("SchoolClass", backref=db.backref("exams", lazy="dynamic"))
    subject = db.relationship("Subject", backref=db.backref("exams", lazy="dynamic"))
    results = db.relationship("ExamResult", back_populates="exam", lazy="dynamic", cascade="all, delete-orphan")


class ExamResult(db.Model):
    __tablename__ = "exam_result"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False, index=True)
    marks_obtained = db.Column(db.Numeric(10, 2), nullable=True)
    grade = db.Column(db.String(10), nullable=True)
    remarks = db.Column(db.String(256), nullable=True)

    exam = db.relationship("Exam", back_populates="results")
    student = db.relationship("Student", backref=db.backref("exam_results", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("exam_id", "student_id", name="uq_exam_result_exam_student"),
    )
