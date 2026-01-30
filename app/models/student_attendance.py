from datetime import date

from app import db


class StudentAttendance(db.Model):
    __tablename__ = "student_attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="present")  # present, absent, late
    remarks = db.Column(db.String(256), nullable=True)

    student = db.relationship("Student", backref=db.backref("attendances", lazy="dynamic"))

    __table_args__ = (
        db.Index("ix_student_attendance_student_date", "student_id", "date", unique=True),
    )
