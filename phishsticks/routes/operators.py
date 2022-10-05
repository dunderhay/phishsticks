import datetime
from flask import redirect, render_template, flash, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..extensions import db, app
from ..forms.webforms import OperatorForm, CurrentOperatorForm
from ..models.models import Operator


@app.route("/operators")
@login_required
def operators():
    form = OperatorForm()
    operators = Operator.query.order_by(Operator.date_added)
    return render_template(
        "operator/operators.html",
        operators=operators,
        form=form,
    )


@app.route("/operator/create", methods=["GET", "POST"])
@login_required
def add_operator():
    username = None
    form = OperatorForm()
    if form.validate_on_submit():
        username_exists = Operator.query.filter_by(username=form.username.data).first()
        if username_exists != None:
            flash("Operator name already exists.", "danger")
            return redirect(request.referrer)
        if len(form.password.data) < 16:
            flash("Password must be minimum of 16 characters", "danger")
            return redirect(request.referrer)
        elif username_exists is None:
            try:
                hashed_pwd = generate_password_hash(
                    form.password.data, method="pbkdf2:sha256", salt_length=16
                )
                operator = Operator(
                    username=form.username.data, password_hash=hashed_pwd
                )
                db.session.add(operator)
                db.session.commit()
            except:
                flash("Unknown error creating operator.", "danger")
                return redirect(request.referrer)
        form.username.data = ""
        form.password.data = ""
        flash("Operator successfully created.", "success")
    else:
        flash("Passwords must match.", "danger")
    return redirect(request.referrer)


@app.route("/operator/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_operator(id):
    form = OperatorForm()
    operator_to_update = Operator.query.get_or_404(id)
    if operator_to_update.id == current_user.id:
        return redirect(url_for("settings"))
    if request.method == "POST":
        if form.validate_on_submit():
            # TODO: test this with POST request directly to default user
            if operator_to_update.id == current_user.id:
                return redirect(url_for("settings"))
            if len(form.password.data) < 16:
                flash("Password must be minimum of 16 characters", "danger")
                return redirect(request.referrer)
            if not request.form["password"] == request.form["confirm_password"]:
                flash("Passwords must match.", "danger")
                return redirect(request.referrer)
            username_exists = Operator.query.filter_by(
                username=form.username.data
            ).first()
            if username_exists and not (
                username_exists.username == operator_to_update.username
            ):
                flash("Operator name already exists.", "danger")
                return redirect(request.referrer)
            if not username_exists or (
                username_exists.username == operator_to_update.username
            ):
                operator_to_update.username = request.form["username"]
                operator_to_update.password_hash = generate_password_hash(
                    request.form["password"], method="pbkdf2:sha256", salt_length=16
                )
            try:
                db.session.commit()
                flash("Operator successfully updated.", "success")
            except:
                flash("Error updating operator.", "success")
            return redirect(request.referrer)
    return render_template(
        "operator/edit_operator.html",
        form=form,
        operator_to_update=operator_to_update,
        id=id,
    )


# TODO: still seems to check verify_password before other conditions... weird
@app.route("/operator/edit/current", methods=["POST"])
@login_required
def edit_current_operator():
    current_operator = Operator.query.get_or_404(current_user.id)
    form = CurrentOperatorForm()
    if form.validate_on_submit():
        if len(form.password.data) < 16:
            flash("Password must be minimum of 16 characters", "danger")
            return redirect(request.referrer)
        if not request.form["password"] == request.form["confirm_password"]:
            flash("Passwords must match.", "danger")
            return redirect(request.referrer)
        username_exists = Operator.query.filter_by(username=form.username.data).first()
        if username_exists and not (
            username_exists.username == current_operator.username
        ):
            flash("Operator name already exists.", "danger")
            return redirect(request.referrer)
        if not username_exists or (
            username_exists.username == current_operator.username
        ):
            if not current_operator.verify_password(request.form["current_password"]):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("settings"))
            current_operator.username = request.form["username"]
            current_operator.password_hash = generate_password_hash(
                request.form["password"], method="pbkdf2:sha256", salt_length=16
            )
            try:
                db.session.commit()
                flash("Operator updated successfully.", "success")
            except:
                flash("Unknown error updating operator", "danger")
            return redirect(request.referrer)
    else:
        # TODO: showing wtf validation errors on settings page isn't working
        flash("Passwords must match.", "danger")
        return redirect(request.referrer)


@app.route("/operator/delete/<int:id>")
@login_required
def delete_operator(id):
    operator_to_delete = Operator.query.get_or_404(id)
    if operator_to_delete.id == current_user.id:
        flash("Cannot delete your own account.", "danger")
        return redirect(request.referrer)
    try:
        db.session.delete(operator_to_delete)
        db.session.commit()
        flash("Operator successfully deleted.", "success")
    except:
        flash("Error deleting operator.", "danger")
    return redirect(request.referrer)
