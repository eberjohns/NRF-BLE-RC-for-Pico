import board, busio, digitalio, time, usb_hid, struct
from nrf_lite import NRFLite
from hid_gamepad import Gamepad
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

time.sleep(2.0)

# 1. Init I2C/ADS1115
i2c = busio.I2C(board.GP5, board.GP4)
ads = ADS.ADS1115(i2c)
channels = [AnalogIn(ads, i) for i in range(4)]
led = digitalio.DigitalInOut(board.GP7)
led.direction = digitalio.Direction.OUTPUT

# 2. Init SPI/Radio
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)
csn, ce = digitalio.DigitalInOut(board.GP21), digitalio.DigitalInOut(board.GP17)
nrf = NRFLite(spi, csn, ce)
# nrf.open_tx_pipe(b"1Node")
nrf.open_tx_pipe(b'\xe7\xe7\xe7\xe7\xe7')

# 3. Init Gamepad
gp = Gamepad(usb_hid.devices)

def map_val(val):
    # Map 16-bit ADC to -100 to 100 for the car
    scaled = int((val / 26400) * 200 - 100)
    return max(min(scaled, 100), -100)

print("🎮 JARVIS REMOTE ONLINE (HID + Radio)")

while True:
    try:
        # Read Sticks
        steering = map_val(channels[3].value) # A3
        throttle = map_val(channels[0].value) # A0
        
        # Update PC Gamepad
        gp.move_joysticks(x=steering, y=throttle)

        # Send to Car
        packet = struct.pack("<bbbb", steering, throttle, 0, 0)
        nrf.send(packet)
        led.value = not led.value

        print(f"S: {steering:>4} T: {throttle:>4}", end='\r')
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(0.1)
    
    time.sleep(0.02) # 50Hz update
