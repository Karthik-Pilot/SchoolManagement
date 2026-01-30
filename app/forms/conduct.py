from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional


class ConductCertificateForm(FlaskForm):
    type = SelectField(
        "Type",
        choices=[("conduct", "Conduct"), ("certificate", "Certificate")],
        validators=[DataRequired()],
    )
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    issue_date = DateField("Issue Date", validators=[Optional()], format="%Y-%m-%d")
