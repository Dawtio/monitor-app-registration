from adal import AuthenticationContext
from datetime import datetime
from prometheus_client import start_http_server, Counter
import requests
import os
import time

const_format_date = "%Y-%m-%d"
c = Counter('secret_to_watch', 'Secret of App Registration to monitor', ['appName', 'secretName', 'expire_in', 'expire_at', 'status'])


def days_between(d1, d2):
    d1 = datetime.strptime(d1, const_format_date)
    d2 = datetime.strptime(d2, const_format_date)
    return abs((d2 - d1).days)

def connect_to_ad_and_get_informations(app_object_id, headers):
    res = requests.get('https://graph.microsoft.com/v1.0/applications/' + app_object_id, headers=headers).json()
    parse_secret(res['passwordCredentials'], res['displayName'].lower().replace('-', '_'))


def parse_secret(creds, appName):
    for items in creds:
        sec = {}
        # Fill Metrics Infos
        for key in items:
            if key == "displayName":
                sec["name"] = items[key]
            if key == "endDateTime":
                sec["expire_at"], sec["status"], sec["expire_in"] = parse_expiration_date(items[key])
        # Write Metrics Infos
        c.labels(appName, sec["name"], sec["expire_in"], sec["expire_at"], sec["status"]).inc()


def parse_expiration_date(date):
    date_expire = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    date_now = datetime.now()
    expire = date_expire.strftime(const_format_date)
    now = date_now.strftime(const_format_date)
    diff = days_between(now, expire)
    status, expire_str = analyse_expiration_date(date_now, date_expire, diff)
    return expire, status, expire_str


def analyse_expiration_date(date_now, date_expire, diff):
    status = ""
    expire = ""
    if date_expire > date_now:
        expire = str(diff)
        if diff <= 14:
            status = "Expire Soon"
        else:
            status = "Valid"
    else:
        expire = "-" + str(diff)
        status = "Expired"
    return status, expire + " days."


def get_token_from_graph_api():
    AZURE_AD_APP_TENANT = os.getenv('AZURE_AD_APP_TENANT')
    AZURE_AD_APP_ID = os.getenv('AZURE_AD_APP_ID')
    AZURE_AD_APP_SECRET = os.getenv('AZURE_AD_APP_SECRET')
    auth_context = AuthenticationContext(
        authority=f'https://login.microsoftonline.com/' + AZURE_AD_APP_TENANT
    )
    token = auth_context.acquire_token_with_client_credentials(
        resource="https://graph.microsoft.com/",
        client_id=AZURE_AD_APP_ID,
        client_secret=AZURE_AD_APP_SECRET,
    )
    return token['accessToken']

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate metrics.
    while True:
        headers = {'Authorization': 'Bearer ' + get_token_from_graph_api()}
        app_to_watch_object_id = os.getenv('AZURE_APP_TO_WATCH').split(" ")
        for id in app_to_watch_object_id:
            connect_to_ad_and_get_informations(id, headers)
        # Run the process once a day
        time.sleep(86400)
