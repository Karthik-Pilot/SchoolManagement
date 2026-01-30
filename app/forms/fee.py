from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange


def coerce_int_or_none(x):
    if x is None or x == "":
        return None
    return int(x)


class FeeStructureForm(FlaskForm):
    class_id = SelectField("Class", coerce=coerce_int_or_none, validators=[DataRequired()])
    fee_type = StringField("Fee Type", validators=[DataRequired()], description="e.g. tuition, transport")
    amount = DecimalField("Amount", places=2, validators=[DataRequired(), NumberRange(min=0)])
    academic_year = StringField("Academic Year", validators=[DataRequired()], default="2024-2025")
    term = StringField("Term", validators=[Optional()], description="e.g. Q1, Q2, Semester 1")


class FeePaymentForm(FlaskForm):
    student_id = SelectField("Student", coerce=coerce_int_or_none, validators=[DataRequired()])
    fee_structure_id = SelectField("Fee Structure", coerce=coerce_int_or_none, validators=[DataRequired()])
    amount_paid = DecimalField("Amount Paid", places=2, validators=[DataRequired(), NumberRange(min=0)])
    payment_date = DateField("Payment Date", validators=[DataRequired()], format="%Y-%m-%d")
    receipt_no = StringField("Receipt No", validators=[Optional()])
    payment_mode = StringField("Payment Mode", validators=[Optional()], description="e.g. cash, card")
