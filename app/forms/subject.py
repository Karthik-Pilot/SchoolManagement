from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional


class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired()])
    code = StringField("Code", validators=[Optional()])
