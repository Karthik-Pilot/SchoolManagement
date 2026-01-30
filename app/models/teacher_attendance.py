from datetime import date

from app import db


class TeacherAttendance(db.Model):
    __tablename__ = "teacher_attendance"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="present")  # present, absent, late
    remarks = db.Column(db.String(256), nullable=True)

    teacher = db.relationship("Teacher", backref=db.backref("attendances", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("teacher_id", "date", name="uq_teacher_attendance_teacher_date"),
    )
