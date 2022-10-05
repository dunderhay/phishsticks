import datetime
from flask import redirect, render_template, flash, request
from flask_login import login_required
from ..extensions import db, app
from ..models.models import UIConfig, DeviceToken
from ..utils import checkUserCodeAuth


@app.route("/dashboard")
@login_required
def dashboard():
    uiconfig = UIConfig.query.get_or_404(1)
    if uiconfig.showexpiredcodes == False:
        # show only valid (not expired) user codes
        devicetokens = DeviceToken.query.filter(
            DeviceToken.usercode_lifespan >= datetime.datetime.now()
        )
    elif uiconfig.showexpiredcodes == True:
        # show all user codes
        devicetokens = DeviceToken.query.order_by(DeviceToken.issued_at)
    return render_template(
        "dashboard/dashboard.html",
        devicetokens=devicetokens,
    )


@app.route("/devicetoken/<int:id>")
@login_required
def view_devicetoken(id):
    devicetokendetails = DeviceToken.query.get_or_404(id)
    uiconfig = UIConfig.query.filter(UIConfig.name == "default").first()
    return render_template(
        "dashboard/devicetoken.html",
        devicetokendetails=devicetokendetails,
        uiconfig=uiconfig,
    )


@app.route("/devicetoken/checkauth/<int:id>", methods=["GET", "POST"])
@login_required
def checkauth_devicetoken(id):
    devicetokendetails = DeviceToken.query.get_or_404(id)
    authcheck = checkUserCodeAuth(devicetokendetails.device_code)
    if authcheck[0] == True:
        auth_data = authcheck[1]
        devicetokendetails.auth_status = "authenticated"
        devicetokendetails.auth_scope = auth_data["scope"]
        devicetokendetails.auth_access_token = auth_data["access_token"]
        devicetokendetails.auth_refresh_token = auth_data["refresh_token"]
        try:
            db.session.commit()
            flash("Device token authentication details updated.", "success")
        except:
            flash("Unknown error device code authentication details.", "danger")
    elif authcheck[0] == False:
        flash(f"No authentication update: {authcheck[1]}", "danger")
    return redirect(request.referrer)
