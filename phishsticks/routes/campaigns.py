import re
import datetime
from flask import redirect, render_template, flash, request
from flask_login import login_required
from flask_mail import Message, Mail
from ..extensions import db, app
from ..forms.webforms import CampaignForm
from ..models.models import Campaign, EmailTemplate, SenderProfile, Group, DeviceToken
from ..utils import fetchNewDeviceToken


@app.route("/campaigns")
@login_required
def campaigns():
    campaigns = Campaign.query.order_by(Campaign.date_added)
    form = CampaignForm()
    emailtemplates = EmailTemplate.query.order_by(EmailTemplate.date_added)
    senderprofiles = SenderProfile.query.order_by(SenderProfile.date_added)
    targetgroups = Group.query.order_by(Group.date_added)
    return render_template(
        "campaign/campaigns.html",
        campaigns=campaigns,
        form=form,
        emailtemplates=emailtemplates,
        senderprofiles=senderprofiles,
        targetgroups=targetgroups,
    )


@app.route("/campaign/create", methods=["GET", "POST"])
@login_required
def add_campaign():
    form = CampaignForm()
    # TODO form validation
    if request.method == "POST":
        campaignexists = Campaign.query.filter_by(name=form.campaignname.data).first()
        print(form.campaignname.data)
        if campaignexists != None:
            flash("Campaign already exists.", "danger")
            return redirect(request.referrer)
        elif campaignexists is None:
            campaign = Campaign(
                name=form.campaignname.data,
                emailtemplate_id=request.form["emailtemplateoption"],
                senderprofile_id=request.form["senderprofileoption"],
                group_id=request.form["targetgroupoption"],
            )
            form.campaignname.data = ""
            try:
                db.session.add(campaign)
                db.session.commit()
                flash("Campaign successfully created.", "success")
            except:
                flash("Unknown error adding campaign.", "danger")
    return redirect(request.referrer)


@app.route("/campaign/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_campaign(id):
    emailtemplates = EmailTemplate.query.order_by(EmailTemplate.date_added)
    senderprofiles = SenderProfile.query.order_by(SenderProfile.date_added)
    targetgroups = Group.query.order_by(Group.date_added)
    form = CampaignForm()
    campaign_to_update = Campaign.query.get_or_404(id)
    if request.method == "POST":
        campaign_to_update.name = request.form["campaignname"]
        campaign_to_update.emailtemplate_id = request.form["emailtemplateoption"]
        campaign_to_update.senderprofile_id = request.form["senderprofileoption"]
        campaign_to_update.group_id = request.form["targetgroupoption"]
        try:
            db.session.commit()
            flash("Campaign successfully created.", "success")
        except:
            flash("Unknown error adding campaign.", "danger")
        return redirect(request.referrer)
    return render_template(
        "campaign/edit_campaign.html",
        form=form,
        campaign_to_update=campaign_to_update,
        emailtemplates=emailtemplates,
        senderprofiles=senderprofiles,
        targetgroups=targetgroups,
    )


@app.route("/campaign/delete/<int:id>")
@login_required
def delete_campaign(id):
    campaign_to_delete = Campaign.query.get_or_404(id)
    try:
        db.session.delete(campaign_to_delete)
        db.session.commit()
        flash("Campaign successfully deleted.", "success")
    except:
        flash("Error deleting campaign.", "danger")
    return redirect(request.referrer)


extra_headers = {
    "X-Priority": "1",
    "X-MSMail-Priority": "1",
    "Mime-Version": "IGNORE",
    "Received": "IGNORE",
    "X-Mailer": "IGNORE",
    "X-Originating-IP": "IGNORE",
}


@app.route("/campaign/start/<int:id>")
@login_required
def start_campaign(id):
    campaign_to_start = Campaign.query.get_or_404(id)
    emailtemplate = EmailTemplate.query.get_or_404(campaign_to_start.emailtemplate_id)
    senderprofile = SenderProfile.query.get_or_404(campaign_to_start.senderprofile_id)
    group = Group.query.get_or_404(campaign_to_start.group_id)
    updatedemail = emailtemplate.body
    # Setup email sender profile details
    app.config["MAIL_SERVER"] = senderprofile.mail_host
    app.config["MAIL_PORT"] = senderprofile.mail_port
    app.config["MAIL_USE_TLS"] = senderprofile.mail_use_tls
    app.config["MAIL_USE_SSL"] = senderprofile.mail_use_ssl
    app.config["MAIL_USERNAME"] = senderprofile.mail_username
    app.config["MAIL_PASSWORD"] = senderprofile.mail_password
    # Get a new token and send phishing email to each target
    mail = Mail(app)
    with mail.connect() as conn:
        for target in group.targets:
            # Get new token and write to database
            devicetoken_data = fetchNewDeviceToken()
            user_code = devicetoken_data["user_code"]
            device_code = devicetoken_data["device_code"]
            expires_in = devicetoken_data["expires_in"]
            interval = devicetoken_data["interval"]
            issued_at = datetime.datetime.now()
            usercode_lifespan = issued_at + datetime.timedelta(seconds=int(expires_in))
            new_devicetoken = DeviceToken(
                user_code=user_code,
                device_code=device_code,
                expires_in=expires_in,
                interval=interval,
                issued_at=issued_at,
                usercode_lifespan=usercode_lifespan,
            )
            try:
                db.session.add(new_devicetoken)
                target.devicetokens.append(new_devicetoken)
                db.session.commit()
                flash("New device token successfully created.", "success")
            except:
                flash("Unknown error adding new device token.", "danger")
            # Update the email template to sub out the user variables (first & last name, and token)
            updatedemail = re.sub(
                r"\{\{\.(first_name)\}\}", target.first_name, updatedemail
            )
            updatedemail = re.sub(
                r"\{\{\.(last_name)\}\}", target.last_name, updatedemail
            )
            updatedemail = re.sub(
                r"\{\{\.(position)\}\}", target.position, updatedemail
            )
            updatedemail = re.sub(r"\{\{\.(usercode)\}\}", user_code, updatedemail)
            # Send phishing email to each target
            msg = Message(
                recipients=[target.email],
                sender=senderprofile.mail_default_sender,
                html=updatedemail,
                subject=emailtemplate.subject,
                extra_headers=extra_headers,
            )
            try:
                conn.send(msg)
                flash("Phishing emails successfully sent.", "success")
            except Exception as e:
                flash("Error sending phishing emails - " + str(e), "danger")
    return redirect(request.referrer)
