import requests
import json

session = requests.Session()
base_url = 'http://raspberrypi.local:8581/api'

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
    url = base_url + f'/accessories/4e7c0b7fa75d76f73a0cc14028fe05c1f4ba50716c4cfb00f32566f57a3c286c'
    payload = {
        "characteristicType": "On",
        "value": "1"
    }
    r = session.put(url, data=payload)
    return r
