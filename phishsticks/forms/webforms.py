from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    EmailField,
    BooleanField,
    TextAreaField,
)
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms.widgets import PasswordInput
from flask_wtf.file import FileField, FileAllowed, FileRequired


class EmailTemplateForm(FlaskForm):
    name = StringField(
        "Template Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Template Name"},
    )
    subject = StringField(
        "Email Subject",
        validators=[DataRequired()],
        render_kw={"placeholder": "Subject"},
    )
    body = CKEditorField("Body", validators=[DataRequired()])
    submit = SubmitField("Save Template")


class TargetForm(FlaskForm):
    firstname = StringField(
        "First Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "First Name"},
    )
    lastname = StringField(
        "Last Name", validators=[DataRequired()], render_kw={"placeholder": "Last Name"}
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Not a valid email address."),
        ],
        render_kw={"placeholder": "foo@example.com"},
    )
    position = StringField(
        "Position", validators=[DataRequired()], render_kw={"placeholder": "Position"}
    )
    submit = SubmitField("Add Target")


class GroupForm(FlaskForm):
    name = StringField(
        "Group Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Group Name"},
    )
    submit = SubmitField("Create Group")


class UploadForm(FlaskForm):
    input_file = FileField(
        "",
        validators=[
            FileRequired(message="No file selected."),
            FileAllowed(["csv"], message="Must be a csv file."),
        ],
    )
    submit = SubmitField(label="Import Targets")


class SenderProfileForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired()], render_kw={"placeholder": "Profile Name"}
    )
    mailprofiledefaultsender = StringField(
        "From",
        validators=[DataRequired()],
        render_kw={"placeholder": "First Last <foo@example.com>"},
    )
    mailprofilehost = StringField(
        "Host",
        validators=[DataRequired()],
        render_kw={"placeholder": "smtp.example.com"},
    )
    mailprofileport = StringField(
        "Port", validators=[DataRequired()], render_kw={"placeholder": "587"}
    )
    mailprofileusername = StringField(
        "Username", validators=[DataRequired()], render_kw={"placeholder": "Username"}
    )
    mailprofilepassword = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Password"},
        widget=PasswordInput(hide_value=False),
    )
    submit = SubmitField("Create Profile")


class CampaignForm(FlaskForm):
    campaignname = StringField(
        "Name", validators=[DataRequired()], render_kw={"placeholder": "Campaign Name"}
    )
    campaigntemplate = StringField("Email Template", validators=[DataRequired()])
    campaignsenderprofile = StringField("Sender Profile", validators=[DataRequired()])
    campaignvictims = StringField("Target Group", validators=[DataRequired()])
    submit = SubmitField("Create Campaign")


class OperatorForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=16, message="Password must be minimum of 16 characters"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=16, message="Password must be minimum of 16 characters."),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Create Operator")


class CurrentOperatorForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=16, message="Password must be minimum of 16 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=16, message="Password must be minimum of 16 characters."),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Save Changes")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired()], render_kw={"placeholder": "username"}
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"placeholder": "password"}
    )
    submit = SubmitField("Login")


class DeviceTokenConfigForm(FlaskForm):
    client_id = StringField(
        "Client ID",
        validators=[DataRequired()],
        render_kw={"placeholder": "d3590ed6-52b3-4102-aeff-aad2292ab01c"},
    )
    resource = StringField(
        "Resource",
        validators=[DataRequired()],
        render_kw={"placeholder": "https://graph.microsoft.com"},
    )
    submit = SubmitField("Save Changes")


class UIConfigForm(FlaskForm):
    showexpiredcodes = BooleanField("[Dashboard] - show expired device tokens")
    showusercodeauthrefresh = BooleanField(
        "[Device Tokens] - show manual authentication check button"
    )
    submit = SubmitField("Save Changes")


class SendTestEmail(FlaskForm):
    recipient = StringField(
        "Recipient",
        validators=[DataRequired()],
        render_kw={"placeholder": "foo@example.com"},
    )
    message = TextAreaField(
        "Email Body",
        validators=[DataRequired()],
        render_kw={"placeholder": "This is a test message"},
    )
    submit = SubmitField("Send Test Email")
