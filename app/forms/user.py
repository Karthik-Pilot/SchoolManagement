from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Optional()])  # Optional on edit
    role = SelectField(
        "Role",
        choices=[
            ("student", "Student"),
            ("teacher", "Teacher"),
            ("head_teacher", "Head Teacher"),
            ("super_admin", "Super Admin"),
        ],
        validators=[DataRequired()],
    )
    linked_id = IntegerField("Linked ID (Student/Teacher)", validators=[Optional()])
