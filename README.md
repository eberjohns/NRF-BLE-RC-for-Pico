# Remote control solutions for Pico microcontroller(BLE & NRF24l01)

## 1. BLE(Bluetooth Low Energy) option:
BLE is available only for pico w/pico 2w(the wireless variants of the pico)


There are 2 options:
- Phone as Remote: Use Dabble app in mobile to control, use the joystick mode. Only code for receiver is needed given under pico_w folder. Connect to 'PicoRC' in Dabble.
- Dedicated remote: The remote will be a proxy and the transmission will be handled by phone itself as Dabble doesn't support external remote input. Open the bridge.html page in phone and turn on bluetooth and connect to 'PicoRC' and connect the remote(which has the pico and 2 joysticks connected to ADS115 module) to phone using cable to read input.

## 2. NRF24L01 module option:
Should have 2 nrf24l01 modules and picos, one for transmission and another set at receiver end.

Remote:
- Pico with CircuitPython
- nrf24l01 transmission module
- Joysticks connected to ADS115 module

Receiver:
- Pico with MicroPython
- nrf24l01 receiver module
- Motor drivers(TB6612FNG or BTS7960)

**Indicator** - 
When the remote connects(the signals reach the receiver), the pico's lights switch from blinking to static on receiver end.

## Schematics:
**(Make sure for NRF modules, MISO, MOSI & SCK pin connections don't change)**

### Remote Schematics:

ADS115 connections:
- VDD - 3.3v
- GND - GND
- SCL - GP4
- SDA - GP5
- A01 - Joystick 1 VRx
- A02 - Joystick 1 VRy
- A03 - Joystick 2 VRx
- A04 - Joystick 2 VRy

NRF24L01 connections:
- VDD - 3.3v
- GND - GND
- MISO - GP16
- MOSI - GP19
- SCK - GP18
- CE - GP17
- CSN - GP21
- IRQ - NOT NEEDED

### Receiver Schematics:

**1. Green board for single TB6612FNG and dual BTS7960**
- NRF24L01 connections:
    - VDD - 3.3v
    - GND - GND
    - MISO - GP16
    - MOSI - GP19
    - SCK - GP18
    - CE - GP17
    - CSN - GP20
    - IRQ - NOT NEEDED

- TB6612FNG connections:
    - VCC - 3.3
    - STBY - 3.3
    - GND - GND
    - APWM - 6
    - AIN1 - 8
    - AIN2 - 9
    - BIN1 - 11
    - BIN2 - 10
    - BPWM - 12
    - A01 - Right motor terminal 1
    - A02 - Right motor terminal 2
    - B01 - Left motor terminal 1
    - B02 - Left motor terminal 2

- BTS7960 connections:
    - VCC - 3.3v
    - GND - GND
    - R_EN - 3.3v
    - L_EN - 3.3v
    - LPWM(Right BTS) - 2
    - RPWM(Right BTS) - 3
    - LPWM(Left BTS) - 4
    - RPWM(Left BTS) - 5

**2. Brown board for BTS7960 alone**
- NRF24L01 connections:
    - VDD - 3.3v
    - GND - GND
    - MISO - GP16
    - MOSI - GP19
    - SCK - GP18
    - CE - GP20
    - CSN - GP17
    - IRQ - NOT NEEDED

- BTS7960 connections:
    - VCC - 3.3v
    - GND - GND
    - R_EN - 3.3v
    - L_EN - 3.3v
    - LPWM(Right BTS) - 12
    - RPWM(Right BTS) - 13
    - LPWM(Left BTS) - 14
    - RPWM(Left BTS) - 15
