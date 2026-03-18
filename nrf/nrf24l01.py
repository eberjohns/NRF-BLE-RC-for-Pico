# nrf24l01.py - MicroPython driver for the nRF24L01+
import time
from machine import Pin, SPI

class NRF24L01:
    def __init__(self, spi, csn, ce, channel=76, payload_size=32):
        self.spi = spi
        self.csn = csn
        self.ce = ce
        self.channel = channel
        self.payload_size = payload_size
        self.csn.init(Pin.OUT, value=1)
        self.ce.init(Pin.OUT, value=0)
        self._init_radio()

    def _init_radio(self):
        time.sleep_ms(5)
        self._write_reg(0x00, 0x0C) # CONFIG: EN_CRC, CRCO
        self._write_reg(0x01, 0x00) # EN_AA: Disable Auto Ack for simplicity
        self._write_reg(0x03, 0x03) # SETUP_AW: 5 bytes
        self._write_reg(0x04, 0x03) # SETUP_RETR: 250us, 3 retries
        self._write_reg(0x05, self.channel)
        self._write_reg(0x06, 0x07) # RF_SETUP: 1Mbps, 0dBm
        self._write_reg(0x11, self.payload_size) # RX_PW_P0

    def _write_reg(self, reg, val):
        self.csn.value(0)
        self.spi.write(bytearray([0x20 | reg, val]))
        self.csn.value(1)

    def _read_reg(self, reg):
        self.csn.value(0)
        self.spi.write(bytearray([reg]))
        val = self.spi.read(1)[0]
        self.csn.value(1)
        return val

    def open_rx_pipe(self, pipe_id, address):
        self.csn.value(0)
        self.spi.write(bytearray([0x20 | (0x0A + pipe_id)]))
        self.spi.write(address)
        self.csn.value(1)

    def start_listening(self):
        val = self._read_reg(0x00)
        self._write_reg(0x00, val | 0x03) # PWR_UP, PRIM_RX
        self.ce.value(1)
        time.sleep_us(130)

    def any(self):
        return not (self._read_reg(0x17) & 0x01) # FIFO_STATUS: RX_EMPTY

    def recv(self):
        self.csn.value(0)
        self.spi.write(bytearray([0x61])) # R_RX_PAYLOAD
        buf = self.spi.read(self.payload_size)
        self.csn.value(1)
        self._write_reg(0x07, 0x40) # Clear RX_DR flag
        return buf
