from datetime import datetime

from app import db


class SchoolClass(db.Model):
    __tablename__ = "school_class"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)  # e.g. "Class 10"
    academic_year = db.Column(db.String(20), nullable=False, default="2024-2025")

    students = db.relationship("Student", back_populates="school_class", lazy="dynamic")
    subjects = db.relationship(
        "Subject",
        secondary="class_subject",
        back_populates="classes",
        lazy="dynamic",
    )

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
