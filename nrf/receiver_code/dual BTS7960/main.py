import machine, time, struct
from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01

led = Pin("LED", Pin.OUT)

# --- 🛠️ BTS7960 MOTOR SETUP ---
# Pins: Left (LPWM=14, RPWM=15) | Right (LPWM=12, RPWM=13)
# Note: L_EN and R_EN on the BTS drivers should be tied to 3.3V
def init_bts(lp_pin, rp_pin):
    lp = PWM(Pin(lp_pin)); lp.freq(15000) # 15kHz for quiet Johnson motors
    rp = PWM(Pin(rp_pin)); rp.freq(15000)
    return lp, rp

l_lpwm, l_rpwm = init_bts(14, 15)
r_lpwm, r_rpwm = init_bts(12, 13)

def apply_bts(speed, lpwm, rpwm):
    # Apply your 50% Power limit for safety
    speed = max(min(speed, 100), -100) * 0.5 
    duty = int(abs(speed) / 100 * 65535)
    
    if speed >= 0: # Forward logic
        rpwm.duty_u16(duty)
        lpwm.duty_u16(0)
    else:          # Reverse logic
        rpwm.duty_u16(0)
        lpwm.duty_u16(duty)

# --- RADIO SETUP ---
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
nrf = NRF24L01(spi, Pin(17), Pin(20), payload_size=4) # CSN, CE

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
            print(buf)
            # Unpack the packet (S, T, 0, 0)
            s, t, _, _ = struct.unpack("<bbbb", buf)
#             print(s,t)
        
            l_speed = t + s
            r_speed = t - s
            # Apply to BTS7960 Drivers
            apply_bts(l_speed, l_lpwm, l_rpwm)
            apply_bts(r_speed, r_lpwm, r_rpwm)
    
        if time.ticks_diff(time.ticks_ms(), last_sig) > 300:
            apply_bts(0, l_lpwm, l_rpwm)
            apply_bts(0, r_lpwm, r_rpwm)
            led.toggle()
            time.sleep(0.1)

try:
    run()
except KeyboardInterrupt:
    apply_bts(0, l_lpwm, l_rpwm)
    apply_bts(0, r_lpwm, r_rpwm)
