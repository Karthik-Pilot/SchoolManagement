from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.String(20),
        nullable=False,
        default="student",
    )  # student, teacher, head_teacher, super_admin
    linked_id = db.Column(db.Integer, nullable=True)  # student_id or teacher_id
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_super_admin(self):
        return self.role == "super_admin"

    @property
    def is_head_teacher(self):
        return self.role == "head_teacher"

    @property
    def is_teacher(self):
        return self.role in ("teacher", "head_teacher")

    @property
    def is_student(self):
        return self.role == "student"

    def can_manage_users(self):
        return self.role in ("super_admin", "head_teacher")
