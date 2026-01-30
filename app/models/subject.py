from app import db


class Subject(db.Model):
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=True, index=True)

    classes = db.relationship(
        "SchoolClass",
        secondary="class_subject",
        back_populates="subjects",
        lazy="dynamic",
    )
    teachers = db.relationship(
        "Teacher",
        secondary="teacher_subject",
        back_populates="subjects",
        lazy="dynamic",
    )

    def __str__(self):
        return self.name or self.code or ""
