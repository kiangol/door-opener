# ESP8266 door opener

This firmware replaces the Raspberry Pi Python process. It reads the LDR
voltage through the NodeMCU A0 analog input, takes two readings, and posts
`{ "value": <average> }` to the Home Assistant webhook when both readings are
below the threshold.

## Setup

1. Install the ESP8266 board package in the Arduino IDE.
2. Select a NodeMCU 1.0 (ESP-12E Module) board.
3. Copy `config.h.example` to `config.h`.
4. Set the Wi-Fi credentials and Home Assistant webhook URL in `config.h`.
5. Connect the LDR voltage output to A0.
6. Upload `door_opener.ino` and open the serial monitor at 115200 baud.

Use a fixed IP address for Home Assistant in the webhook URL unless mDNS
resolution of `homeassistant.local` is known to work on the network.

## Electrical notes

- The ESP8266 ADC is 0-1.0 V on the bare chip. Many NodeMCU boards include a
  divider that allows 0-3.3 V on A0; verify your specific board before wiring.
- Never apply more than the A0 voltage limit to the board.
- Use a voltage-divider LDR circuit with a stable 0-3.3 V output.

## Calibration

Record the two readings in the serial monitor with the door in both relevant
light conditions, then set `ACTIVATION_THRESHOLD` in `config.h` between those
values. Lower readings are treated as activation.
