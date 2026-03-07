import machine, bluetooth, time
from ble_uart_peripheral import BLEUART

# Onboard LED
led = machine.Pin("LED", machine.Pin.OUT)

# ================= 🛡️ YOUR PINS =================
# R_PINS: [PWM, IN1, IN2] -> 5, 4, 3
# L_PINS: [PWM, IN1, IN2] -> 2, 1, 0
R_PINS = [5, 4, 3] 
L_PINS = [2, 1, 0] 
SAFE_LIMIT = 0.5 # 50% Power

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

# ================= 🔵 HYBRID DECODER =================
ble = bluetooth.BLE()
uart = BLEUART(ble, name="PicoRC")

def parse_dabble():
    raw = uart.read()
    if not raw or len(raw) < 7: return
    
    try:
        # Check Header
        if raw[0] == 0xFF and raw[1] == 0x01:
            # BUTTONS are in raw[5] for your version
            btns = raw[5]
            
            # THROTTLE LOGIC
            # Triangle is usually bit 2 (0x04), Cross is usually bit 5 (0x20)
            thrust = 0
            if btns & 0x04: thrust = 100   # Triangle Pressed
            elif btns & 0x20: thrust = -100 # Cross Pressed
            
            # STEERING LOGIC (Index 6)
            steer_raw = raw[6] if raw[6] < 128 else raw[6] - 256
            steering = steer_raw * 14.2 
            
            # Deadzone (ignore tiny movements)
            if abs(steering) < 10: steering = 0

            # 🏎️ MIXING FOR RACE CAR FEEL
            # Both moving + turning at the same time
            l_speed = thrust + steering
            r_speed = thrust - steering
            
            apply_motor(l_speed, l_pwm, l_in1, l_in2)
            apply_motor(r_speed, r_pwm, r_in1, r_in2)
            
            # DEBUG: Uncomment this if it still doesn't work to see button hex
            # print("Btn Byte:", hex(btns), "Thrust:", thrust)
            
    except: pass

uart.irq(handler=parse_dabble)

print("🏎️ PicoRC: Triangle=Fwd, Cross=Rev, Stick=Turn")

while True:
    if not uart.is_connected():
        apply_motor(0, l_pwm, l_in1, l_in2)
        apply_motor(0, r_pwm, r_in1, r_in2)
        led.toggle()
        time.sleep(0.1)
    else:
        led.value(1)
        time.sleep(0.1)
