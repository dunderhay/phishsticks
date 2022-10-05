import requests
import datetime
from threading import Thread
from time import sleep
from .extensions import db, app
from .models.models import DeviceToken, DeviceTokenConfig


# Helper functions
@app.template_filter("datetimeformat")
def datetimeformat(value, format="%d-%m-%Y - %I:%M:%S %p"):
    return value.strftime(format)


def fetchNewDeviceToken():
    devicetokenconfig = DeviceTokenConfig.query.filter(
        DeviceTokenConfig.name == "default"
    ).first()
    usercode_url = (
        "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"
    )
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    }
    usercode_payload = {
        "client_id": devicetokenconfig.client_id,
        "resource": devicetokenconfig.resource,
    }
    usercode_response = requests.post(
        usercode_url, headers=headers, data=usercode_payload
    )
    if usercode_response.status_code == 200:
        usercode_data = usercode_response.json()
        return usercode_data
    else:
        print("[!] Something went wrong getting an initial device token.")


# Poll Microsoft for user authentication
# TODO: Handle the expected response errors better (https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code#expected-errors)
def checkUserCodeAuth(device_code):
    devicetokenconfig = DeviceTokenConfig.query.filter(
        DeviceTokenConfig.name == "default"
    ).first()
    auth_url = "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    }
    auth_payload = {
        "client_id": devicetokenconfig.client_id,
        "resource": devicetokenconfig.resource,
        "code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    time = datetime.datetime.now()
    time.strftime("%H:%M:%S")
    auth_response = requests.post(auth_url, headers=headers, data=auth_payload)
    auth_data = auth_response.json()
    print(auth_payload)
    if auth_response.status_code == 200:
        print("[+] User successfully authenticated!")
        auth_scope = auth_data["scope"]
        auth_accesstoken = auth_data["access_token"]
        auth_freshtoken = auth_data["refresh_token"]
        auth_resource = auth_data["resource"]
        print(
            f"[+] Scope: {auth_scope}\n[+] Resource: {auth_resource}\n[+] Access Token: {auth_accesstoken} \n[+] Refresh Token: {auth_freshtoken}"
        )
        return True, auth_data
    elif auth_response.status_code == 400:
        auth_error = auth_data["error"]
        print(
            f"[*] Status: {auth_error} at {time.hour:02d}:{time.minute:02d}:{time.second:02d}",
            end="\r",
        )
        return False, auth_data


# TODO: check if this is acceptable / flask way to do threads..
def background_updatetokenexpirationstatus():
    app.app_context().push()
    while True:
        devicetokens = DeviceToken.query.filter(DeviceToken.expired == False)
        for devicetoken in devicetokens:
            if devicetoken.usercode_lifespan <= datetime.datetime.now():
                devicetoken.expired = True
                try:
                    db.session.commit()
                except:
                    pass
        sleep(5)


daemon = Thread(
    target=background_updatetokenexpirationstatus,
    daemon=True,
    name="bg_updatetokenexpirationstatus",
)
daemon.start()


def background_updatetokenauthstatus():
    app.app_context().push()
    while True:
        devicetokens = DeviceToken.query.filter(
            DeviceToken.auth_status == "pending", DeviceToken.expired == False
        )
        for devicetoken in devicetokens:
            authcheck = checkUserCodeAuth(devicetoken.device_code)
            if authcheck[0] == True:
                auth_data = authcheck[1]
                devicetoken.auth_status = "authenticated"
                devicetoken.auth_scope = auth_data["scope"]
                devicetoken.auth_access_token = auth_data["access_token"]
                devicetoken.auth_refresh_token = auth_data["refresh_token"]
                try:
                    db.session.commit()
                except:
                    pass
        sleep(5)


daemon = Thread(
    target=background_updatetokenauthstatus,
    daemon=True,
    name="bg_updatetokenauthstatus",
)
daemon.start()
