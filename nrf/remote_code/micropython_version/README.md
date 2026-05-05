# MicroPython remote

This version uses micropython so that we can utilise both the cores:
- one does the joystick reading, math and nrf transmission
- second handles the oled screen updations

## Pin connections on the pico:
**OLED**
- sda = GP0
- scl = GP1

**NRF**
- MISO - GP16
- MOSI - GP19
- SCK - GP18
- CE - GP17
- CSN - GP21
- IRQ - NOT NEEDED

**ADS115**
- SCL - GP4
- SDA - GP5

**Trigger Left**
- GP10

**Trigger Right**
- GP22

## Additional libraries:

In Thonny, go to Tools > Manage Packages and install this library:

` ssd1306 (The standard MicroPython OLED driver) `

`main.py`, `nrf_lite.py`, `ads1x15.py` all goes in the root folder. 