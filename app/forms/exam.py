from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange


def coerce_int_or_none(x):
    if x is None or x == "":
        return None
    return int(x)


class ExamForm(FlaskForm):
    name = StringField("Exam Name", validators=[DataRequired()])
    exam_type = SelectField(
        "Type",
        choices=[("exam", "Exam"), ("test", "Test")],
        validators=[DataRequired()],
    )
    class_id = SelectField("Class", coerce=coerce_int_or_none, validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=coerce_int_or_none, validators=[DataRequired()])
    max_marks = DecimalField("Max Marks", places=2, validators=[DataRequired(), NumberRange(min=0)], default=100)
    exam_date = DateField("Exam Date", validators=[Optional()], format="%Y-%m-%d")
