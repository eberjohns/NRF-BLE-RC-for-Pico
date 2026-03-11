import board
import time
import analogio
import usb_hid
from hid_gamepad import Gamepad 

# Initialize the manual Gamepad
gp = Gamepad(usb_hid.devices)

# Hardware Setup:
# Left Joystick VRy (Throttle) -> Pico A0 (GP26)
# Right Joystick VRx (Steering) -> Pico A1 (GP27)
throttle_axis = analogio.AnalogIn(board.A0) 
steering_axis = analogio.AnalogIn(board.A1) 

def map_value(value):
    """Maps 0-65535 to -127 to 127"""
    # Inverse may be needed depending on your wiring (use 127 - ... if inverted)
    return int((value / 65535) * 254 - 127)

# Calibration: Center values aren't always 32768
DEADZONE = 15 

print("Joystick Remote Active!")

while True:
    # 1. Read raw values
    t_raw = throttle_axis.value
    s_raw = steering_axis.value

    # 2. Map to HID range (-127 to 127)
    t_val = map_value(t_raw)
    s_val = map_value(s_raw)

    # 3. Apply Deadzone (Prevents car from 'creeping' when sticks are idle)
    if abs(t_val) < DEADZONE: t_val = 0
    if abs(s_val) < DEADZONE: s_val = 0

    # 4. Send to USB
    # x/y coordinates for the phone to interpret
    try:
        gp.move_joysticks(x=s_val, y=t_val)
    except Exception as e:
        print("Error sending HID:", e)
    
    # Fast enough for RC (10ms delay = 100Hz refresh)
    time.sleep(0.01)
