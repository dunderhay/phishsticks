from flask import redirect, render_template, flash, request
from flask_login import login_required
from ..extensions import db, app
from ..forms.webforms import EmailTemplateForm
from ..models.models import EmailTemplate


@app.route("/emailtemplates")
@login_required
def emailtemplates():
    emailtemplates = EmailTemplate.query.order_by(EmailTemplate.date_added)
    return render_template(
        "emailtemplate/email_templates.html", emailtemplates=emailtemplates
    )


@app.route("/emailtemplate/create", methods=["GET", "POST"])
@login_required
def add_emailtemplate():
    form = EmailTemplateForm()
    if form.validate_on_submit():
        templatenameexists = EmailTemplate.query.filter_by(name=form.name.data).first()
        if templatenameexists != None:
            flash("Template already exists.", "danger")
            return render_template(
                "emailtemplate/add_email_template.html",
                form=form,
            )
        elif templatenameexists is None:
            emailtemplate = EmailTemplate(
                name=form.name.data, subject=form.subject.data, body=form.body.data
            )
            form.name.data = ""
            form.subject.data = ""
            form.body.data = ""
        try:
            db.session.add(emailtemplate)
            db.session.commit()
            flash("Email template successfully created.", "success")
        except:
            flash("Unknown error adding template to database.", "danger")
    return render_template(
        "emailtemplate/add_email_template.html",
        form=form,
    )


@app.route("/emailtemplates/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_emailtemplate(id):
    form = EmailTemplateForm()
    emailtemplate_to_update = EmailTemplate.query.get_or_404(id)
    # pass the body value into the page
    form.body.data = emailtemplate_to_update.body
    if request.method == "POST":
        if form.validate_on_submit():
            emailtemplate_to_update.name = request.form["name"]
            emailtemplate_to_update.subject = request.form["subject"]
            emailtemplate_to_update.body = request.form["body"]
            # pass the body value into the page again to reflect the update when the page reloads
            form.body.data = emailtemplate_to_update.body
        try:
            db.session.commit()
            flash("Email template successfully updated.", "success")
            return render_template(
                "emailtemplate/edit_email_template.html",
                form=form,
                emailtemplate_to_update=emailtemplate_to_update,
                id=id,
            )
        except:
            flash("Unknown error updating email template.", "danger")
    return render_template(
        "emailtemplate/edit_email_template.html",
        form=form,
        emailtemplate_to_update=emailtemplate_to_update,
        id=id,
    )


@app.route("/emailtemplate/delete/<int:id>")
@login_required
def delete_emailtemplate(id):
    emailtemplate_to_delete = EmailTemplate.query.get_or_404(id)
    try:
        db.session.delete(emailtemplate_to_delete)
        db.session.commit()
        flash("Email template successfully deleted.", "success")
    except:
        flash("Error deleting email template.", "danger")
    return redirect(request.referrer)
