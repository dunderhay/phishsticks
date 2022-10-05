from flask import redirect, url_for, render_template, flash, request
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import check_password_hash
from ..extensions import login_manager, app, app_version
from ..forms.webforms import LoginForm
from ..models.models import Operator


login_manager.login_view = "login"


@login_manager.user_loader
def load_operator(operator_id):
    return Operator.query.get(int(operator_id))


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.form.get("next")
    if current_user.is_authenticated:
        if next_url:
            return redirect(next_url)
        return redirect(url_for("dashboard"))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            operator = Operator.query.filter_by(username=form.username.data).first()
            if operator:
                if check_password_hash(operator.password_hash, form.password.data):
                    login_user(operator)
                    if next_url:
                        return redirect(next_url)
                    return redirect(url_for("dashboard"))
                else:
                    flash("Invalid user name or password.")
            else:
                flash("Invalid user name or password.")
        return render_template("auth/login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Operator logged out.")
    return redirect(url_for("login"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
