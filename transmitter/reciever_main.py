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

# ================= 🔵 SERIAL DECODER =================
ble = bluetooth.BLE()
uart = BLEUART(ble, name="PicoRC")

def parse_serial():
    raw = uart.read()
    if not raw: return
    
    try:
        # Decode the byte data to a string (e.g., "0,100")
        data_str = raw.decode().strip()
        print(f"Received: {data_str}") # Debugging in Thonny
        
        # Expecting format: "steering,throttle"
        parts = data_str.split(',')
        if len(parts) == 2:
            steering = float(parts[0]) # -100 to 100
            throttle = float(parts[1]) # -100 to 100

            # 🏎️ DIFFERENTIAL MIXING
            l_speed = throttle + steering
            r_speed = throttle - steering
            
            apply_motor(l_speed, l_pwm, l_in1, l_in2)
            apply_motor(r_speed, r_pwm, r_in1, r_in2)
            
    except Exception as e:
        print(f"Parse Error: {e}")

uart.irq(handler=parse_serial)

print("🏎️ RACER READY: Expecting 'steering,throttle' via Bluetooth Serial")

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