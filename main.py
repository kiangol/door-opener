import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import RPi.GPIO as GPIO

import homebridge as hb

LOG_DIR = os.path.join('/home', 'pi', 'logs')
LOG_FILENAME = os.path.join(LOG_DIR, "log.out")
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10240000, backupCount=3)
logging.basicConfig(
    handlers=[handler],
    format='%(asctime)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    level=logging.DEBUG,
)

GPIO.setmode(GPIO.BOARD)

# define the pin that goes to the circuit
ldr_pin = 7
# Higher value -> higher sensitivity. Default 1100
activation_threshold = 3000
# Time to wait in seconds before activating switch again,
# if call is still in progress.
call_timeout = os.environ.get('DOOROPENER_RETRY_TIMEOUT')
if call_timeout is None:
    call_timeout = 30
else:
    call_timeout = int(call_timeout)


def rc_time(pin_to_circuit=ldr_pin):
    count = 0

    # Output on the pin for
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.5)

    # Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)

    # Count until the pin goes high
    while GPIO.input(pin_to_circuit) == GPIO.LOW:
        if count > 10000:
            return count
        count += 1

    return count


def should_activate(val, threshold=activation_threshold):
    return val < threshold


def main():
    last_activated = datetime.now()
    logging.info("Starting reading...")
    while True:
        try:
            now = datetime.now()

            v1 = rc_time()
            v2 = rc_time()
            val = (v1 + v2) / 2

            logging.debug(f"V1:{v1} | V2:{v2} - avg:{val}")

            if should_activate(v1) and should_activate(v2):
                time_since_last_activation = (now - last_activated).seconds
                if time_since_last_activation < call_timeout:
                    logging.info(f"Skipping. Last:{last_activated}, {time_since_last_activation} s ago")
                    continue

                logging.info(f"Activating switch {val} | (v1:{v1},v2:{v2})")
                logging.info(hb.send_notification_hass().content)
                last_activated = datetime.now()

        except KeyboardInterrupt as k:
            logging.info(k)
        except Exception as ex:
            logging.error("Error occurred", e)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(e)
        exit(1)
