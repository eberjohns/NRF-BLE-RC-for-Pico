import bluetooth
import struct
import time
from micropython import const

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x03)
_ADV_TYPE_UUID32_COMPLETE = const(0x05)
_ADV_TYPE_UUID128_COMPLETE = const(0x07)
_ADV_TYPE_UUID16_MORE = const(0x02)
_ADV_TYPE_UUID32_MORE = const(0x04)
_ADV_TYPE_UUID128_MORE = const(0x06)
_ADV_TYPE_APPEARANCE = const(0x19)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY,)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX),)

class BLEUART:
    def __init__(self, ble, name="Pico-RC", rxbuf=100):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_callback = None
        self._payload = self._ad_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        if event == 1: # _IRQ_CENTRAL_CONNECT
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == 2: # _IRQ_CENTRAL_DISCONNECT
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == 3: # _IRQ_GATTS_WRITE
            if self._rx_callback:
                self._rx_callback()

    def irq(self, handler):
        self._rx_callback = handler

    def read(self):
        return self._ble.gatts_read(self._rx_handle)

    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_write(self._tx_handle, data)
            self._ble.gatts_notify(conn_handle, self._tx_handle)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _ad_payload(self, limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
        payload = bytearray()
        def _append(adv_type, value):
            nonlocal payload
            payload += struct.pack("BB", len(value) + 1, adv_type) + value
        _append(_ADV_TYPE_FLAGS, struct.pack("B", (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))
        if name: _append(_ADV_TYPE_NAME, name)
        if services:
            for s in services:
                b = bytes(s)
                if len(b) == 2: _append(_ADV_TYPE_UUID16_COMPLETE, b)
                elif len(b) == 4: _append(_ADV_TYPE_UUID32_COMPLETE, b)
                elif len(b) == 16: _append(_ADV_TYPE_UUID128_COMPLETE, b)
        if appearance: _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))
        return payload
