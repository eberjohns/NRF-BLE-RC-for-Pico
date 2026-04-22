import board, busio, digitalio, time, usb_hid, struct
from nrf_lite import NRFLite
from hid_gamepad import Gamepad
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

time.sleep(1.0)

# 1. Init HARDWARE I2C for ADS1115 (GP5/GP4)
i2c_ads = busio.I2C(board.GP5, board.GP4)
ads = ADS.ADS1115(i2c_ads)
channels = [AnalogIn(ads, i) for i in range(4)]

# 2. Init LED, Radio, and Gamepad
led = digitalio.DigitalInOut(board.GP7)
led.direction = digitalio.Direction.OUTPUT

spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)
csn, ce = digitalio.DigitalInOut(board.GP21), digitalio.DigitalInOut(board.GP17)
nrf = NRFLite(spi, csn, ce)
nrf.open_tx_pipe(b'\xe7\xe7\xe7\xe7\xe7')

gp = Gamepad(usb_hid.devices)

def map_axis(val):
    """Maps joystick -100 to 100"""
    # Using 26400 as the max 16-bit ADC value for your sticks
    scaled = int((val / 26400) * 200 - 100)
    return max(min(scaled, 100), -100)

def map_limit(val):
    """Maps speed limit joystick 0 to 100"""
    scaled = int((val / 26400) * 100)
    return max(min(scaled, 100), 0)

print("🚀 JARVIS REMOTE: ACTIVE")

while True:
    try:
        # 1. Read Raw Values
        raw_s = -(map_axis(channels[0].value)) 
        raw_t = map_axis(channels[1].value)
        speed_limit = map_limit(channels[3].value)

        # 2. Apply Sensitivity Scaling
        # formula: output = input * (limit / 100)
        steering = int(raw_s * (speed_limit / 100.0))
        throttle = int(raw_t * (speed_limit / 100.0))

        # 3. Output to PC HID (Optional)
        gp.move_joysticks(x=steering, y=throttle)

        # 4. Send to Car via NRF
        # We pack 4 bytes: [Steering, Throttle, 0, 0]
        packet = struct.pack("<bbbb", steering, throttle, 0, 0)
        nrf.send(packet)
        print(packet)

        # Blink LED to show transmission is happening
        led.value = not led.value

        # Small delay to keep the loop at approx 50Hz
        time.sleep(0.01)

    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(0.1)
