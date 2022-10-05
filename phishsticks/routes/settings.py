from flask import redirect, render_template, flash, request
from flask_login import login_required, current_user
from ..extensions import db, app, app_version
from ..forms.webforms import CurrentOperatorForm, UIConfigForm, DeviceTokenConfigForm
from ..models.models import Operator, UIConfig, DeviceTokenConfig


@app.route("/settings")
@login_required
def settings():
    current_operator = Operator.query.get_or_404(current_user.id)
    devicetokenconfig = DeviceTokenConfig.query.filter(
        DeviceTokenConfig.name == "default"
    ).first()
    uiconfig = UIConfig.query.filter(UIConfig.name == "default").first()
    operator_form = CurrentOperatorForm()
    devicetokenconfig_form = DeviceTokenConfigForm()
    uiconfig_form = UIConfigForm()
    return render_template(
        "settings/settings.html",
        app_version=app_version,
        current_operator=current_operator,
        devicetokenconfig=devicetokenconfig,
        uiconfig=uiconfig,
        operator_form=operator_form,
        devicetokenconfig_form=devicetokenconfig_form,
        uiconfig_form=uiconfig_form,
    )


@app.route("/devicetoken/config/update", methods=["POST"])
@login_required
def edit_devicetoken_config():
    devicetokenconfig = DeviceTokenConfig.query.filter(
        DeviceTokenConfig.name == "default"
    ).first()
    form = DeviceTokenConfigForm()
    if form.validate_on_submit():
        devicetokenconfig.client_id = form.client_id.data
        devicetokenconfig.resource = form.resource.data
        try:
            db.session.commit()
            flash("Device token configuration successfully updated.", "success")
        except:
            flash("Unknown error device token configuration.", "danger")
    return redirect(request.referrer)


@app.route("/ui/config/update", methods=["POST"])
@login_required
def edit_ui_config():
    uiconfig = UIConfig.query.filter(UIConfig.name == "default").first()
    form = UIConfigForm()
    if form.validate_on_submit():
        if request.form.get("showexpiredswitch"):
            uiconfig.showexpiredcodes = True
        else:
            uiconfig.showexpiredcodes = False
        if request.form.get("showusercodeauthrefresh"):
            uiconfig.showusercodeauthrefresh = True
        else:
            uiconfig.showusercodeauthrefresh = False
        try:
            db.session.commit()
            flash("User interface configuration successfully updated.", "success")
        except:
            flash("Unknown error user interface configuration.", "danger")
    return redirect(request.referrer)
