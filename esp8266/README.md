# ESP8266 door opener

This firmware replaces the Raspberry Pi Python process. It keeps the same
behavior: discharge the LDR circuit, measure how long the input remains LOW,
take two readings, and post `{ "value": <average> }` to the Home Assistant
webhook when both readings are below the threshold.

## Setup

1. Install the ESP8266 board package in the Arduino IDE.
2. Select a NodeMCU 1.0 (ESP-12E Module) board.
3. Copy `config.h.example` to `config.h`.
4. Set the Wi-Fi credentials and Home Assistant webhook URL in `config.h`.
5. Set `LDR_PIN` to the GPIO connected to the existing LDR circuit.
6. Upload `door_opener.ino` and open the serial monitor at 115200 baud.

Use a fixed IP address for Home Assistant in the webhook URL unless mDNS
resolution of `homeassistant.local` is known to work on the network.

## Electrical notes

- The ESP8266 GPIO is 3.3 V only. Do not expose it to 5 V.
- `LDR_PIN` is configured as an output LOW while discharging, then as an
  input while measuring. The existing Raspberry Pi RC LDR circuit can be
  reused only if it is electrically safe for the ESP8266.
- GPIO5 is NodeMCU pin D1 and is the default because it normally does not
  interfere with boot. Avoid changing it to GPIO0, GPIO2, or GPIO15 without
  checking the circuit's boot-time levels.

## Calibration

The threshold is based on software loop counts, so ESP8266 readings will not
match Raspberry Pi counts exactly. Record the two readings in the serial
monitor with the door in both relevant light conditions, then adjust
`ACTIVATION_THRESHOLD` in `config.h`.
