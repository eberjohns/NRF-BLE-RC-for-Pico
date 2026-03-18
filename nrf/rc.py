import machine, time, struct
from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01

led = Pin("LED", Pin.OUT)

# --- MOTOR SETUP ---
R_PINS, L_PINS = [5, 4, 3], [2, 1, 0]
def init_motor(pins):
    pwm = PWM(Pin(pins[0])); pwm.freq(5000) 
    return pwm, Pin(pins[1], Pin.OUT), Pin(pins[2], Pin.OUT)

r_pwm, r_in1, r_in2 = init_motor(R_PINS)
l_pwm, l_in1, l_in2 = init_motor(L_PINS)

def apply_motor(speed, pwm, in1, in2):
    speed = max(min(speed, 100), -100) * 0.5 # 50% Power limit
    in1.value(1 if speed >= 0 else 0)
    in2.value(0 if speed >= 0 else 1)
    pwm.duty_u16(int(abs(speed) / 100 * 65535))

# --- RADIO SETUP ---
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
nrf = NRF24L01(spi, Pin(17), Pin(20), payload_size=4)

# SYNC SETTINGS
nrf._write_reg(0x01, 0x00) # Disable Auto-Ack
nrf._write_reg(0x06, 0x07) # 1Mbps
nrf.open_rx_pipe(0, b'\xe7\xe7\xe7\xe7\xe7') # Matching Remote Test Address
nrf.start_listening()

print("🏎️ JARVIS CAR: LISTENING...")
last_sig = time.ticks_ms()

def run():
    global last_sig
    
    while True:
        if nrf.any():
            last_sig = time.ticks_ms()
            led.value(1)
        
            buf = nrf.recv()
            # Unpack the packet (S, T, 0, 0)
            s, t, _, _ = struct.unpack("<bbbb", buf)
        
            l_speed = t + s
            r_speed = t - s
            apply_motor(l_speed, l_pwm, l_in1, l_in2)
            apply_motor(r_speed, r_pwm, r_in1, r_in2)
    
        if time.ticks_diff(time.ticks_ms(), last_sig) > 300:
            apply_motor(0, l_pwm, l_in1, l_in2)
            apply_motor(0, r_pwm, r_in1, r_in2)
            led.toggle()
            time.sleep(0.1)

run()