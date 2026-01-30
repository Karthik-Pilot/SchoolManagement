from datetime import datetime, date

from app import db


# Many-to-many: teacher <-> subject
teacher_subject = db.Table(
    "teacher_subject",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id"), primary_key=True),
)

# Many-to-many: class <-> subject (which subjects are taught in which class)
class_subject = db.Table(
    "class_subject",
    db.Column("class_id", db.Integer, db.ForeignKey("school_class.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id"), primary_key=True),
)


class Teacher(db.Model):
    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(40), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(40), nullable=True)
    join_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects = db.relationship(
        "Subject",
        secondary=teacher_subject,
        back_populates="teachers",
        lazy="dynamic",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"
