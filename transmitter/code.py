import board
import time
import analogio
import usb_hid
from hid_gamepad import Gamepad 

# Initialize the manual Gamepad
gp = Gamepad(usb_hid.devices)

# Setup Joysticks
# Joy 1 (Left): VRx -> A0 (Yaw/Steer), VRy -> A1 (Throttle)
# Joy 2 (Right): VRx -> A2 (Roll/Slide), VRy -> Not Connected
joy1_x = analogio.AnalogIn(board.A0) 
joy1_y = analogio.AnalogIn(board.A1) 
joy2_x = analogio.AnalogIn(board.A2) 

def map_val(raw):
    # Maps 0-65535 to -127 to 127
    val = int((raw / 65535) * 254 - 127)
    # Deadzone logic: if the stick is near center, make it exactly 0
    if abs(val) < 12: 
        return 0
    return val

print("Transmitter Active: 3 Axes + 1 Fake")

while True:
    # Read and map values
    # Added negative sign to joy1_x if your steering is reversed
    s_val = map_val(joy1_x.value)  # Steering / Yaw
    t_val = map_val(joy1_y.value)  # Throttle
    r_val = map_val(joy2_x.value)  # Roll / Extra
    
    # Send all 4 axes to the HID device (Phone/PC)
    # x/y is stick 1, z/r_z is stick 2
    gp.move_joysticks(
        x = s_val, 
        y = t_val, 
        z = r_val, 
        r_z = 0    # The 4th axis you'll add later with ADS1115
    )
    
    # 10ms delay (100Hz) is the "sweet spot" for RC response
    time.sleep(0.01)
