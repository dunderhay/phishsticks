import csv
from flask import redirect, render_template, flash, request
from flask_login import login_required
from ..extensions import db, app
from ..forms.webforms import GroupForm, TargetForm, UploadForm
from ..models.models import Group, Target


@app.route("/targets")
@login_required
def targets():
    groups = Group.query.order_by(Group.date_added)
    group_form = GroupForm()
    # TODO: filter count by only uses in specific group (if you want to show group count..)
    # target_count = Target.query.filter(Target.groups.any(name=group_to_update.name)).count()
    return render_template(
        "targets/targets.html",
        groups=groups,
        group_form=group_form,
    )


@app.route("/target/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_target(id):
    target_to_update = Target.query.get_or_404(id)
    update_target_form = TargetForm()
    if request.method == "POST":
        target_to_update.first_name = update_target_form.firstname.data
        target_to_update.last_name = update_target_form.lastname.data
        target_to_update.email = update_target_form.email.data
        target_to_update.position = update_target_form.position.data
        try:
            db.session.commit()
            flash("Target successfully updated.", "success")
        except:
            flash("Error updating target.", "danger")
    return redirect(request.referrer)


@app.route("/target/delete/<int:id>")
@login_required
def delete_target(id):
    target_to_delete = Target.query.get_or_404(id)
    try:
        db.session.delete(target_to_delete)
        db.session.commit()
        flash("Target successfully deleted.", "success")
    except:
        flash("Error deleting target.", "danger")
    return redirect(request.referrer)


@app.route("/group/create", methods=["GET", "POST"])
@login_required
def add_group():
    group_form = GroupForm()
    if group_form.validate_on_submit():
        groupexists = Group.query.filter_by(name=group_form.name.data).first()
        if groupexists != None:
            flash("Target group with that name already exists.", "danger")
            return redirect(request.referrer)
        elif groupexists is None:
            group = Group(name=group_form.name.data)
            group_form.name.data = ""
        try:
            db.session.add(group)
            db.session.commit()
            flash("Target group successfully created.", "success")
        except:
            flash("Unknown error adding target group.", "danger")
    return redirect(request.referrer)


@app.route("/group/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_group(id):
    group_to_update = Group.query.get_or_404(id)
    targets = Target.query.filter(Target.groups.any(name=group_to_update.name))
    target_form = TargetForm()
    update_target_form = TargetForm()
    upload_form = UploadForm()
    return render_template(
        "targets/edit_group.html",
        targets=targets,
        group_to_update=group_to_update,
        target_form=target_form,
        update_target_form=update_target_form,
        upload_form=upload_form,
    )


@app.route("/group/edit/<int:id>/add/target", methods=["POST"])
@login_required
def add_target_to_group(id):
    group_to_update = Group.query.get_or_404(id)
    target_form = TargetForm()
    if target_form.validate_on_submit():
        target = Target(
            first_name=target_form.firstname.data,
            last_name=target_form.lastname.data,
            email=target_form.email.data,
            position=target_form.position.data,
        )
        target_form.firstname.data = ""
        target_form.lastname.data = ""
        target_form.email.data = ""
        target_form.position.data = ""
        try:
            db.session.add(target)
            target.groups.append(group_to_update)
            db.session.commit()
            flash("Target successfully added.", "success")
        except:
            flash("Unknown error adding target.", "danger")
    return redirect(request.referrer)


@app.route("/group/delete/<int:id>")
@login_required
def delete_group(id):
    group_to_delete = Group.query.get_or_404(id)
    try:
        db.session.delete(group_to_delete)
        db.session.commit()
        flash("Target group successfully deleted.", "success")
    except:
        flash("Error deleting target group.", "danger")
    return redirect(request.referrer)


ALLOWED_EXTENSIONS = set(["csv"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/group/edit/<int:id>/upload/targets", methods=["POST"])
def upload_targets(id):
    group_to_update = Group.query.get_or_404(id)
    form = UploadForm()
    if request.method == "POST" and form.validate_on_submit():
        input_file = request.files["input_file"]
        if input_file.filename == "":
            flash("No file selected.", "danger")
            return redirect(request.referrer)
        if input_file and allowed_file(input_file.filename):
            csv_data = input_file.read().decode("utf-8")
            rows = csv.reader(csv_data.splitlines())
            header = next(rows)  # skip file header - line 1
            for row in rows:
                target = Target(
                    first_name=row[0],
                    last_name=row[1],
                    email=row[2],
                    position=row[3],
                )
                try:
                    db.session.add(target)
                    target.groups.append(group_to_update)
                    db.session.commit()
                except:
                    flash("Unknown error uploading target.", "danger")
            flash("Targets successfully imported.", "success")
    else:
        flash("File type not allowed - must be a csv file.", "danger")
    return redirect(request.referrer)
