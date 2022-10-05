import os
import secrets
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_migrate import Migrate


app_version = "0.0.3-dev"

app = Flask(__name__)

secret_key = secrets.token_hex(30)
app.config["SECRET_KEY"] = secret_key

db_path = os.path.join(os.path.dirname(__file__), "../db.sqlite")
db_uri = "sqlite:///{}".format(os.path.normpath(db_path))
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
