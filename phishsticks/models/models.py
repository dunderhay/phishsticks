import datetime
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db, app


# Define the Operator data-model.
class Operator(db.Model, UserMixin):
    __tablename__ = "Operator"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.now)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Name %r>" % self.name


# Define the Campaign data-model
class Campaign(db.Model):
    __tablename__ = "Campaign"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.now)
    emailtemplate_id = db.Column(db.Integer, db.ForeignKey("EmailTemplate.id"))
    senderprofile_id = db.Column(db.Integer, db.ForeignKey("SenderProfile.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("Group.id"))


# Define the Email Templates data-model
class EmailTemplate(db.Model):
    __tablename__ = "EmailTemplate"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.now)


# Define the SMTP Sender Profile data-model
class SenderProfile(db.Model):
    __tablename__ = "SenderProfile"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    mail_default_sender = db.Column(db.String(255), nullable=False)
    # TODO: have single host (host:port) line or keep host / port split as below?
    mail_host = db.Column(db.String(100), nullable=False)
    mail_port = db.Column(db.Integer(), nullable=False, default=587)
    mail_username = db.Column(db.String(100), nullable=False)
    mail_password = db.Column(db.String(255), nullable=False)
    mail_use_ssl = db.Column(db.Boolean(), nullable=False, default=False)
    mail_use_tls = db.Column(db.Boolean(), nullable=False, default=True)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.now)


# Define the TargetDeviceToken association table
target_devicetoken = db.Table(
    "target_devicetoken",
    db.Column("target_id", db.Integer, db.ForeignKey("Target.id", ondelete="CASCADE")),
    db.Column(
        "devicetoken_id",
        db.Integer,
        db.ForeignKey("DeviceToken.id", ondelete="CASCADE"),
    ),
)


# Define the TargetGroup association table
target_group = db.Table(
    "target_group",
    db.Column("target_id", db.Integer, db.ForeignKey("Target.id", ondelete="CASCADE")),
    db.Column("group_id", db.Integer, db.ForeignKey("Group.id", ondelete="CASCADE")),
)

# Define the Group data-model
class Group(db.Model):
    __tablename__ = "Group"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.now)
    # Define the relationship to Target via target_group
    # This prevents orphans when deleting a group (no orphan users)
    # TODO: however, cannot have two users with same name in different groups (because email field is unique)
    targets = db.relationship(
        "Target",
        secondary=target_group,
        backref="groups",
        cascade="all,delete-orphan",
        single_parent=True,
    )


# Define the Targets data-model
class Target(db.Model):
    __tablename__ = "Target"
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(
        db.String(100), nullable=False
    )  # TODO: removed unique constraint for now.. (unique=True )
    position = db.Column(db.String(100), nullable=False)


# Define the devicetoken data-model
class DeviceToken(db.Model):
    __tablename__ = "DeviceToken"
    id = db.Column(db.Integer(), primary_key=True)
    user_code = db.Column(db.String(20), nullable=False, unique=True)
    device_code = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime(), nullable=False)
    expires_in = db.Column(db.String(20), nullable=False)
    interval = db.Column(db.String(20), nullable=False)
    usercode_lifespan = db.Column(db.DateTime(), nullable=False)
    expired = db.Column(db.Boolean(), nullable=False, default=False)
    auth_status = db.Column(db.String(30), nullable=False, default="pending")
    auth_scope = db.Column(db.String(255))
    auth_access_token = db.Column(db.String(255))
    auth_refresh_token = db.Column(db.String(255))
    targets = db.relationship(
        "Target", secondary=target_devicetoken, backref="devicetokens", lazy="dynamic"
    )


# Define the devicetoken phishing config data-model
class DeviceTokenConfig(db.Model):
    __tablename__ = "DeviceTokenConfig"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    client_id = db.Column(db.String(255), nullable=False)
    resource = db.Column(db.String(255), nullable=False)


# Define the ui config data-model
class UIConfig(db.Model):
    __tablename__ = "UIConfig"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    showexpiredcodes = db.Column(db.Boolean(), nullable=False, default=True)
    showusercodeauthrefresh = db.Column(db.Boolean(), nullable=False, default=True)


# Create the database
db.create_all(app=app)

# Create default admin user with random password
if not Operator.query.filter(Operator.username == "admin").first():
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(16))
    default_operator = Operator(
        username="admin",
        password_hash=generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        ),
    )
    db.session.add(default_operator)
    db.session.commit()
    print("---------------------------")
    print("---Default login details---")
    print("---------------------------")
    print(f"Username: admin\nPassword: {password}")
    print("---------------------------")


# Create default devicetoken config
if not DeviceTokenConfig.query.filter(DeviceTokenConfig.name == "default").first():
    default_devicetokenconfig = DeviceTokenConfig(
        name="default",
        client_id="d3590ed6-52b3-4102-aeff-aad2292ab01c",
        resource="https://graph.microsoft.com",
    )
    db.session.add(default_devicetokenconfig)
    db.session.commit()
    print("Created default device token config")
    print("---------------------------")


# Create default ui config
if not UIConfig.query.filter(UIConfig.name == "default").first():
    default_uiconfig = UIConfig(
        name="default", showexpiredcodes=True, showusercodeauthrefresh=False
    )
    db.session.add(default_uiconfig)
    db.session.commit()
    print("Created default user interface config")
    print("---------------------------")


# Create default phishing campaign pretext
if not EmailTemplate.query.filter(EmailTemplate.name == "default").first():
    default_phishing_template = EmailTemplate(
        name="default",
        subject="Microsoft Security - Action Required",
        body="""
        <p>Hi {{.first_name}}</p>

        <p>Your device is being logged out of Microsoft Office 365. Please use the following device code to re-link your account.</p>

        <p>Your device code is: {{.usercode}}</p>

        <p>Enter your unique device linking code at the following URL: https://microsoft.com/devicelogin</p>

        <p>Sincerely,<br />
        Microsoft Device Security Team</p>

        <hr />
        <p>Microsoft Corporation | One Microsoft Way, Redmond, WA 98052-6399<br />
        This message was sent from an unmonitored email address. Please do not reply to this message<br />
        Privacy | Legal</p>
        """,
    )
    db.session.add(default_phishing_template)
    db.session.commit()
    print("Created default phishing template")
    print("---------------------------")
