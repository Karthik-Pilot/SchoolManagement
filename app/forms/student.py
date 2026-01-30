from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional


def coerce_int_or_none(x):
    if x is None or x == "":
        return None
    return int(x)


class StudentForm(FlaskForm):
    admission_no = StringField("Admission No", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    dob = DateField("Date of Birth", validators=[Optional()], format="%Y-%m-%d")
    gender = SelectField(
        "Gender",
        choices=[("", ""), ("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[Optional()],
    )
    class_id = SelectField("Class", coerce=coerce_int_or_none, validators=[Optional()])
    section = StringField("Section", validators=[Optional()])
    guardian_name = StringField("Guardian Name", validators=[Optional()])
    guardian_contact = StringField("Guardian Contact", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional()])
    admission_date = DateField("Admission Date", validators=[Optional()], format="%Y-%m-%d")
