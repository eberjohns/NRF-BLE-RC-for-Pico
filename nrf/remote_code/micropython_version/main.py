import machine
from machine import Pin, SPI, I2C, SoftI2C
import _thread
import time
import struct
from nrf_lite import NRFLite
import ads1x15
from ssd1306 import SSD1306_I2C

# --- 1. SHARED STATE & MUTEX LOCK ---
# This dictionary safely passes data from Core 0 to Core 1
telemetry = {"steering": 0, "throttle": 0}
data_lock = _thread.allocate_lock()

# --- 2. CORE 1: OLED DEDICATED THREAD ---
def core1_oled():
    # Hardware I2C0 for OLED
    i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c_oled)
    
    while True:
        # Safely grab the latest data
        with data_lock:
            s = telemetry["steering"]
            t = telemetry["throttle"]
            
        oled.fill(0)
        oled.text("GODS: ACTIVE", 10, 0)
        oled.text("---------------", 0, 10)
        oled.text(f"Steer : {s:>4}", 0, 25)
        oled.text(f"Throt : {t:>4}", 0, 40)
        oled.show()
        
        time.sleep(0.03) # Cap at ~30Hz to avoid I2C spam

# --- 3. CORE 0: INITIALIZATION ---
# SoftI2C for ADS so we don't conflict with I2C0 on GP0/1
i2c_ads = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
ads = ads1x15.ADS1115(i2c_ads, address=0x48)

led = Pin(7, Pin.OUT)
btn_left = Pin(10, Pin.IN, Pin.PULL_UP)
btn_right = Pin(22, Pin.IN, Pin.PULL_UP)

# SPI for NRF
spi = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(21, Pin.OUT)
ce = Pin(17, Pin.OUT)

nrf = NRFLite(spi, csn, ce)
nrf.open_tx_pipe(b'\xe7\xe7\xe7\xe7\xe7')

def map_val(val, scale):
    # Depending on the specific micropython-ads1x15 library, raw values might 
    # differ from CircuitPython. You may need to tweak the 26400 divisor.
    scaled = int((val / 26400) * (scale*2) - scale+1)
    return max(min(scaled, scale), -scale)

# --- 4. START CORE 1 ---
_thread.start_new_thread(core1_oled, ())

# --- 5. CORE 0: MAIN LOOP ---
print("🎮 JARVIS REMOTE ONLINE (Dual Core)")

while True:
    try:
        # Read Sticks A0-right X | A1-right Y | A2-left X | A3-left Y
        raw_steer = ads.read(0) # A0
        raw_throt = ads.read(3) # A3
        
        steering = map_val(raw_steer, 60)
        throttle = map_val(raw_throt, 70)
        
        trigger_l = not btn_left.value()  
        trigger_r = not btn_right.value()
        
        if trigger_l:
            if throttle > -1: throttle += 25
            else: throttle -= 25
        if trigger_r:
            throttle, steering = 0, 0
            
        # Update shared state for OLED safely
        with data_lock:
            telemetry["steering"] = steering
            telemetry["throttle"] = throttle
    
        # Send to Car
        packet = struct.pack("<bbbb", steering, -throttle, 0, 0)
        nrf.send(packet)
        led.toggle() # MicroPython has a native toggle function
        
        print(f"S: {steering:>4} T: {throttle:>4}", end='\r')
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(0.1)
        
    time.sleep(0.02) # 50Hz update
