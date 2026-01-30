from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, Optional, Email


class TeacherForm(FlaskForm):
    employee_id = StringField("Employee ID", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    phone = StringField("Phone", validators=[Optional()])
    join_date = DateField("Join Date", validators=[Optional()], format="%Y-%m-%d")
