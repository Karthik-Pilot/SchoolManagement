from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from wtforms.validators import DataRequired, Optional


def coerce_int_or_none(x):
    if x is None or x == "":
        return None
    return int(x)


class BulkAttendanceForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], format="%Y-%m-%d")
    class_id = SelectField("Class", coerce=coerce_int_or_none, validators=[Optional()])
    section = SelectField("Section", validators=[Optional()])
