from datetime import date

from app import db


class FeeStructure(db.Model):
    __tablename__ = "fee_structure"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"), nullable=False, index=True)
    fee_type = db.Column(db.String(80), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False, default="2024-2025")
    term = db.Column(db.String(20), nullable=True)

    school_class = db.relationship("SchoolClass", backref=db.backref("fee_structures", lazy="dynamic"))
    payments = db.relationship("FeePayment", back_populates="fee_structure", lazy="dynamic")


class FeePayment(db.Model):
    __tablename__ = "fee_payment"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False, index=True)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey("fee_structure.id"), nullable=False, index=True)
    amount_paid = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    receipt_no = db.Column(db.String(60), nullable=True, index=True)
    payment_mode = db.Column(db.String(40), nullable=True)

    student = db.relationship("Student", backref=db.backref("fee_payments", lazy="dynamic"))
    fee_structure = db.relationship("FeeStructure", back_populates="payments")
