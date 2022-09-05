import logging

import RPi.GPIO as GPIO
import time
import homebridge as hb
from datetime import datetime
import logging
from logging import handlers

LOG_FILENAME = "log.out"
formatter = logging.Formatter("%(asctime)s - %(message)s")

handler = handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 * 1024 * 1024, backupCount=2)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

log = logging.getLogger('LOG')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

GPIO.setmode(GPIO.BOARD)

# define the pin that goes to the circuit
ldr_pin = 7


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
        count += 1
        if count > 10000:
            return count

    return count


last_activated = datetime.now()

try:
    log.info("Starting reading...")
    while True:
        now = datetime.now()

        v1, v2 = rc_time(), rc_time()
        val = (v1 + v2) / 2
        log.debug(f"V1:{v1} | V2:{v2} - avg:{val}")

        if v1 < 1200 and v2 < 1200:
            time_since_last_activation = (now - last_activated).seconds
            if time_since_last_activation < 10:
                log.info("Skipping duplicate activation")
                continue

            log.info(f"Activating switch {val} | (v1:{v1},v2:{v2})")
            hb.send_notification()
            last_activated = datetime.now()
            hb.activate_switch()
            time.sleep(1)
            hb.activate_switch()

except KeyboardInterrupt as k:
    log.error("Error occurred", k)
    pass
except Exception as e:
    log.error("Error occurred", e)
finally:
    GPIO.cleanup()
