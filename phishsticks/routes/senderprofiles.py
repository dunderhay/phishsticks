import re
from flask import redirect, render_template, flash, request
from flask_login import login_required
from flask_mail import Message, Mail
from ..extensions import db, app
from ..forms.webforms import SenderProfileForm, SendTestEmail
from ..models.models import SenderProfile


@app.route("/senderprofile")
@login_required
def senderprofile():
    form = SendTestEmail()
    senderprofiles = SenderProfile.query.order_by(SenderProfile.date_added)
    return render_template(
        "senderprofile/sender_profile.html",
        senderprofiles=senderprofiles,
        form=form,
    )


@app.route("/senderprofile/create", methods=["GET", "POST"])
@login_required
def add_senderprofile():
    form = SenderProfileForm()
    if form.validate_on_submit():
        senderprofileexists = SenderProfile.query.filter_by(name=form.name.data).first()
        if senderprofileexists != None:
            flash("Sender profile already exists.", "danger")
            return render_template(
                "senderprofile/add_sender_profile.html",
                form=form,
            )
        elif senderprofileexists is None:
            transportsecurityoption = request.form["transportsecurity"]
            senderprofile = SenderProfile(
                name=form.name.data,
                mail_default_sender=form.mailprofiledefaultsender.data,
                mail_host=form.mailprofilehost.data,
                mail_port=form.mailprofileport.data,
                mail_username=form.mailprofileusername.data,
                mail_password=form.mailprofilepassword.data,
                mail_use_ssl=transportsecurityoption == "usessl",
                mail_use_tls=transportsecurityoption == "usetls",
            )
            form.name.data = ""
            form.mailprofiledefaultsender.data = ""
            form.mailprofilehost.data = ""
            form.mailprofileport.data = ""
            form.mailprofileusername.data = ""
            form.mailprofilepassword.data = ""
        try:
            db.session.add(senderprofile)
            db.session.commit()
            flash("Sender profile successfully created.", "success")
        except:
            flash("Unknown error adding sender profile.", "danger")
    return render_template(
        "senderprofile/add_sender_profile.html",
        form=form,
    )


@app.route("/senderprofile/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_senderprofile(id):
    form = SenderProfileForm()
    senderprofile_to_update = SenderProfile.query.get_or_404(id)
    if request.method == "POST":
        # TODO: this is so gross - fix this
        if form.validate_on_submit():
            senderprofile_to_update.name = form.name.data
            senderprofile_to_update.mail_default_sender = (
                form.mailprofiledefaultsender.data
            )
            senderprofile_to_update.mail_host = form.mailprofilehost.data
            senderprofile_to_update.mail_port = form.mailprofileport.data
            senderprofile_to_update.mail_username = form.mailprofileusername.data
            senderprofile_to_update.mail_password = form.mailprofilepassword.data
            transportsecurityoption = request.form["transportsecurity"]
            senderprofile_to_update.mail_use_ssl = transportsecurityoption == "usessl"
            senderprofile_to_update.mail_use_tls = transportsecurityoption == "usetls"
        try:
            db.session.commit()
            flash("Sender profile successfully updated.", "success")
        except:
            flash("Unknown error sender profile.", "danger")
    return render_template(
        "senderprofile/edit_sender_profile.html",
        form=form,
        senderprofile_to_update=senderprofile_to_update,
        id=id,
    )


@app.route("/senderprofile/delete/<int:id>")
@login_required
def delete_senderprofile(id):
    senderprofile_to_delete = SenderProfile.query.get_or_404(id)
    try:
        db.session.delete(senderprofile_to_delete)
        db.session.commit()
        flash("Sender profile successfully deleted.", "success")
    except:
        flash("Error deleting sender profile.", "danger")
    return redirect(request.referrer)


@app.route("/sendtestemail/<int:id>", methods=["GET", "POST"])
@login_required
def send_test_email(id):
    form = SendTestEmail()
    if form.validate_on_submit():
        current_senderprofile = SenderProfile.query.get_or_404(id)
        app.config["MAIL_SERVER"] = current_senderprofile.mail_host
        app.config["MAIL_PORT"] = current_senderprofile.mail_port
        app.config["MAIL_USE_TLS"] = current_senderprofile.mail_use_tls
        app.config["MAIL_USE_SSL"] = current_senderprofile.mail_use_ssl
        app.config["MAIL_USERNAME"] = current_senderprofile.mail_username
        app.config["MAIL_PASSWORD"] = current_senderprofile.mail_password
        # TODO: test this, seems like it should work - is it the best way to do it? Probably not
        mail_default_sender_raw = current_senderprofile.mail_default_sender
        mail_default_sender_combined = mail_default_sender_raw.split(" <")
        mail_default_sender_name = mail_default_sender_combined[0]
        mail_default_sender_email = re.search("<(.*)>", mail_default_sender_raw)
        msg = Message(
            "Test Email",
            sender=(mail_default_sender_name, mail_default_sender_email.group(1)),
            recipients=[form.recipient.data],
        )
        msg.html = form.message.data
        mail = Mail(app)
        try:
            mail.send(msg)
            flash("Sent test email.", "success")
        except Exception as e:
            flash("Error sending test email - " + str(e), "danger")
        return redirect(request.referrer)
