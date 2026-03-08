import machine, bluetooth, time
from ble_uart_peripheral import BLEUART

# Onboard LED
led = machine.Pin("LED", machine.Pin.OUT)

# ================= 🛡️ PIN CONFIG =================
R_PINS = [5, 4, 3] # PWM, IN1, IN2
L_PINS = [2, 1, 0] # PWM, IN1, IN2
SAFE_LIMIT = 0.5

def init_motor(pins):
    pwm = machine.PWM(machine.Pin(pins[0])); pwm.freq(5000) 
    return pwm, machine.Pin(pins[1], machine.Pin.OUT), machine.Pin(pins[2], machine.Pin.OUT)

r_pwm, r_in1, r_in2 = init_motor(R_PINS)
l_pwm, l_in1, l_in2 = init_motor(L_PINS)

def apply_motor(speed, pwm, in1, in2):
    speed = max(min(speed, 100), -100) * SAFE_LIMIT
    in1.value(1 if speed >= 0 else 0)
    in2.value(0 if speed >= 0 else 1)
    pwm.duty_u16(int(abs(speed) / 100 * 65535))

# ================= 🔵 PRO DECODER =================
ble = bluetooth.BLE()
uart = BLEUART(ble, name="PicoRC")

def parse_dabble():
    raw = uart.read()
    if not raw or len(raw) < 7: return
    
    try:
        if raw[0] == 0xFF and raw[1] == 0x01:
            # 1. THROTTLE (Triangle/Cross)
            btns = raw[5]
            thrust = 0
            if btns & 0x04: thrust = 100    # Triangle -> Gas
            elif btns & 0x10: thrust = -100 # Cross -> Reverse
            
            # 2. SMOOTH STEERING (Byte 6)
            # Normalizing your 0-127 (Right) and -1 to -128 (Left)
            raw_steer = raw[6]
            if raw_steer >= 128: 
                # Negative range (Left)
                steering = ((raw_steer - 256) / 128) * 100
            else:
                # Positive range (Right)
                steering = (raw_steer / 127) * 100
            
            # Deadzone for the joystick center
            if abs(steering) < 8: steering = 0

            # 🏎️ DIFFERENTIAL MIXING
            # Turning right = Left motor faster, Right motor slower
            l_speed = thrust + steering
            r_speed = thrust - steering
            
            apply_motor(l_speed, l_pwm, l_in1, l_in2)
            apply_motor(r_speed, r_pwm, r_in1, r_in2)
            
    except: pass

uart.irq(handler=parse_dabble)

print("🏎️ RACER READY: Triangle=Gas, Cross=Rev, Stick=Steer")

def run():
    while True:
        if not uart.is_connected():
            apply_motor(0, l_pwm, l_in1, l_in2)
            apply_motor(0, r_pwm, r_in1, r_in2)
            led.toggle()
            time.sleep(0.1)
        else:
            led.value(1)
            time.sleep(0.1)

run()