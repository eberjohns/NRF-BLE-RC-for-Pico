import time

class ADS1115:
    def __init__(self, i2c, address=0x48):
        self.i2c = i2c
        self.address = address
        self.buf = bytearray(2)

    def read(self, channel):
        """Reads a single-ended value from the specified channel (0-3)"""
        if not 0 <= channel <= 3:
            raise ValueError("Channel must be 0, 1, 2, or 3")
        
        # MUX mapping for single-ended reads:
        # 0: 0x4000, 1: 0x5000, 2: 0x6000, 3: 0x7000
        mux = (channel + 4) << 12 
        
        # 0x8000: Start single conversion
        # 0x0200: PGA = +/- 4.096V (Standard for 3.3V joystick reading)
        # 0x0100: Single-shot mode
        # 0x0080: 128 samples per second
        # 0x0003: Disable comparator
        config = 0x8000 | mux | 0x0200 | 0x0100 | 0x0080 | 0x0003
        
        self.buf[0] = (config >> 8) & 0xFF
        self.buf[1] = config & 0xFF
        self.i2c.writeto_mem(self.address, 0x01, self.buf) # Write to Config register
        
        # Wait for conversion to complete (~8ms)
        time.sleep_ms(9)
        
        # Read from Conversion register
        self.i2c.readfrom_mem_into(self.address, 0x00, self.buf)
        val = (self.buf[0] << 8) | self.buf[1]
        
        # Convert to signed 16-bit integer
        if val > 32767:
            val -= 65536
        return val
