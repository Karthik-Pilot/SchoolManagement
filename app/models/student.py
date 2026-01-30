from datetime import datetime, date

from app import db


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(40), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # male, female, other
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"), nullable=True)
    section = db.Column(db.String(20), nullable=True)
    guardian_name = db.Column(db.String(120), nullable=True)
    guardian_contact = db.Column(db.String(40), nullable=True)
    address = db.Column(db.Text, nullable=True)
    admission_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    school_class = db.relationship("SchoolClass", back_populates="students")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.admission_no})"
