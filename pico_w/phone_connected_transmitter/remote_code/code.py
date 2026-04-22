import board
import busio
import usb_hid
import time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C and ADS1115
i2c = busio.I2C(board.GP5, board.GP4)
ads = ADS.ADS1115(i2c)

# Map pins A0-A3
# Drone/Console Standard: 
# A0/A1 = Left Stick (X/Y), A2/A3 = Right Stick (X/Y)
channels = [AnalogIn(ads, i) for i in range(4)]

# Find the Gamepad device
def get_gamepad():
    for device in usb_hid.devices:
        if device.usage_page == 0x01 and device.usage == 0x05:
            return device
    return None

gp_device = get_gamepad()
report = bytearray(6) # 2 bytes buttons + 4 bytes axes

def map_val(val):
    # ADS1115 range (0-26400) to signed byte (-127 to 127)
    scaled = int((val / 26400) * 254 - 127)
    if abs(scaled) < 10: scaled = 0 # Deadzone for jitter
    return max(min(scaled, 127), -127)

print("🎮 Console Mode Active: Testing 4 Axes...")

while True:
    # 1. Read ADS1115
    axes = [map_val(c.value) for c in channels]
    
    # 2. Pack the Report (Byte 0-1: Buttons, Byte 2-5: X, Y, Z, Rz)
    report[0] = 0x00 # Buttons 1-8 (Not used yet)
    report[1] = 0x00 # Buttons 9-16
    report[2] = -(axes[3]) & 0xFF # X
    report[3] = -(axes[0]) & 0xFF # Y
    report[4] = axes[1] & 0xFF # Z
    report[5] = axes[2] & 0xFF # Rz
    
    # 3. Send to PC/Phone
    if gp_device:
        gp_device.send_report(report)
        
    print(f"X:{axes[1]:>4} Y:{axes[0]:>4} RX:{axes[3]:>4} RY:{axes[2]:>4}", end='\r')
    time.sleep(0.01) # 100Hz for ultra-smooth gaming
