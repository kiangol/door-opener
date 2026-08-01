import requests

session = requests.Session()

def send_notification_hass(value=0):
    url = 'http://homeassistant.local:8123/api/webhook/dorapner-I1QiuVIRrMX3XeXHtIxJwZPI'
    r = session.post(url, json={'value': value})
    return r
