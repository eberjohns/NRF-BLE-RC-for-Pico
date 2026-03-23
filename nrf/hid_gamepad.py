# Save this in /lib/hid_gamepad.py
import struct
import time

class Gamepad:
    def __init__(self, devices):
        self._gamepad_device = None
        for dev in devices:
            if dev.usage_page == 0x01 and dev.usage == 0x05:
                self._gamepad_device = dev
                break
        if not self._gamepad_device:
            raise RuntimeError("Could not find Gamepad HID device. Check your boot.py!")
        self._report = bytearray(6)

    def press_buttons(self, *buttons):
        for button in buttons:
            self._report_buttons(button, True)
        self._send()

    def release_buttons(self, *buttons):
        for button in buttons:
            self._report_buttons(button, False)
        self._send()

    def release_all_buttons(self):
        self._report[0] = 0
        self._report[1] = 0
        self._send()

    def move_joysticks(self, x=0, y=0, z=0, r_z=0):
        self._report[2] = self._validate(x)
        self._report[3] = self._validate(y)
        self._report[4] = self._validate(z)
        self._report[5] = self._validate(r_z)
        self._send()

    def _report_buttons(self, button, press):
        if not 1 <= button <= 16:
            raise ValueError("Button must be 1-16")
        button -= 1
        byte_index = button // 8
        bit_index = button % 8
        if press:
            self._report[byte_index] |= (1 << bit_index)
        else:
            self._report[byte_index] &= ~(1 << bit_index)

    def _validate(self, val):
        if not -127 <= val <= 127:
            raise ValueError("Joystick must be -127 to 127")
        return val & 0xFF

    def _send(self):
        self._gamepad_device.send_report(self._report)

