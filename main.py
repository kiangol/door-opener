import logging

import RPi.GPIO as GPIO
import time
import homebridge as hb
from datetime import datetime
import logging
from logging import handlers

LOG_FILENAME = "log.out"
formatter = logging.Formatter("%(asctime)s %(message)s")

handler = handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10*1024*1024, backupCount=2)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

log = logging.getLogger('LOG')
log.setLevel(logging.DEBUG)
log.addHandler(handler)


GPIO.setmode(GPIO.BOARD)

# define the pin that goes to the circuit
pin_to_circuit = 7


def rc_time(pin_to_circuit):
    count = 0

    # Output on the pin for
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.5)

    # Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)

    # Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count


# Catch when script is interrupted, cleanup correctly
last_activated = datetime.now()

try:
    # Main loop
    while True:
        now = datetime.now()
        v1, v2 = rc_time(pin_to_circuit), rc_time(pin_to_circuit)
        val = (v1+v2)/2
        if v1 < 2000 and v2 < 2000:
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
        log.debug(f"V1:{v1} | V2:{v2} -> {val}")
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
