from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SchoolClassForm(FlaskForm):
    name = StringField("Class Name", validators=[DataRequired()], description="e.g. Class 10")
    academic_year = StringField("Academic Year", validators=[DataRequired()], default="2024-2025")
