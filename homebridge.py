import time

import requests
import json

session = requests.Session()
base_url = 'http://raspberrypi.local:8581/api'
switch_id = '14b7ef84237c7d0ee003fce089e7520189575340fa36482aeda5ff581ab8dace'


def get_access_token():
    url = f'{base_url}/auth/login'
    data = {'username': 'admin', 'password': 'admin'}

    r = json.loads(session.post(url=url, data=data).content)
    access_token = r['access_token']
    session.headers.update({
        "Authorization": "Bearer " + access_token
    })


    return access_token


def validate_access_token():
    url = f'{base_url}/auth/check'
    r = session.get(url)

    if r.status_code != "201":
        get_access_token()


def get_accessory(uuid=''):
    url = base_url + f'/accessories/{uuid}'
    r = json.loads(session.get(url).content)
    return r


def send_notification():
    url = 'https://api.pushcut.io/g6V-0NfXxpldSJqfvMgTK/notifications/Arrival'
    r = session.get(url)
    return r


def activate_switch():
    validate_access_token()
    url = base_url + f'/accessories/{switch_id}'
    payload_on = {
        "characteristicType": "On",
        "value": "1"
    }
    payload_off = {
        "characteristicType": "On",
        "value": "0"
    }
    r = session.put(url, data=payload_on)
    time.sleep(0.5)
    r = session.put(url, data=payload_off)
    return r
