from datetime import date

from app import db


class ConductCertificate(db.Model):
    __tablename__ = "conduct_certificate"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, default="conduct")  # conduct, certificate
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(256), nullable=True)

    student = db.relationship("Student", backref=db.backref("conduct_certificates", lazy="dynamic"))
