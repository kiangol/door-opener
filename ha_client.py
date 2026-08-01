import logging
import requests

session = requests.Session()

def send_notification_hass(value=0):
    url = 'http://homeassistant.local:8123/api/webhook/dorapner-I1QiuVIRrMX3XeXHtIxJwZPI'
    r = session.post(url, json={'value': value})
    logging.info("Sent notification to Home Assistant with value " + str(value))
    return r
