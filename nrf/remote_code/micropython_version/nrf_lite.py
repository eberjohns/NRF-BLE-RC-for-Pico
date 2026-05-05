import time
from machine import Pin

class NRFLite:
    def __init__(self, spi, csn, ce, channel=76, payload_size=4):
        self.spi = spi
        self.csn = csn
        self.ce = ce
        self.payload_size = payload_size
        
        # Initialize pins
        self.csn.init(Pin.OUT, value=1)
        self.ce.init(Pin.OUT, value=0)
        
        time.sleep(0.005)
        self._write_reg(0x00, 0x0E) # CONFIG: PWR_UP
        self._write_reg(0x01, 0x00) # Disable Auto-Ack
        self._write_reg(0x03, 0x03) # 5-byte address
        self._write_reg(0x04, 0x00) # No retries
        self._write_reg(0x05, channel)
        self._write_reg(0x06, 0x07) # 1Mbps
        self._write_reg(0x11, payload_size)

    def _write_reg(self, reg, val):
        self.csn.value(0)
        self.spi.write(bytearray([0x20 | reg, val]))
        self.csn.value(1)

    def open_tx_pipe(self, address):
        for reg in [0x0A, 0x10]: # RX_ADDR_P0 and TX_ADDR
            self.csn.value(0)
            self.spi.write(bytearray([0x20 | reg]))
            self.spi.write(address)
            self.csn.value(1)

    def send(self, data):
        self.csn.value(0)
        self.spi.write(bytearray([0xE1])) # Flush TX
        self.csn.value(1)
        
        self.csn.value(0)
        self.spi.write(bytearray([0xA0])) # Write Payload
        self.spi.write(data)
        self.csn.value(1)
        
        self.ce.value(1)
        time.sleep(0.0001)
        self.ce.value(0)
        self._write_reg(0x07, 0x70) # Clear status
