import usb_hid

# Manual definition of a Gamepad device
# Usage Page 1 (Generic Desktop), Usage 5 (Gamepad)
gamepad = usb_hid.Device(
    report_descriptor=bytes((
        0x05, 0x01,  # Usage Page (Generic Desktop)
        0x09, 0x05,  # Usage (Gamepad)
        0xA1, 0x01,  # Collection (Application)
        0x85, 0x01,  # Report ID (1)
        0x05, 0x09,  #   Usage Page (Button)
        0x19, 0x01,  #   Usage Minimum (1)
        0x29, 0x10,  #   Usage Maximum (16)
        0x15, 0x00,  #   Logical Minimum (0)
        0x25, 0x01,  #   Logical Maximum (1)
        0x75, 0x01,  #   Report Size (1)
        0x95, 0x10,  #   Report Count (16)
        0x81, 0x02,  #   Input (Data, Variable, Absolute)
        0x05, 0x01,  #   Usage Page (Generic Desktop)
        0x15, 0x81,  #   Logical Minimum (-127)
        0x25, 0x7F,  #   Logical Maximum (127)
        0x09, 0x30,  #   Usage (X)
        0x09, 0x31,  #   Usage (Y)
        0x09, 0x32,  #   Usage (Z)
        0x09, 0x35,  #   Usage (Rz)
        0x75, 0x08,  #   Report Size (8)
        0x95, 0x04,  #   Report Count (4)
        0x81, 0x02,  #   Input (Data, Variable, Absolute)
        0xC0         # End Collection
    )),
    usage_page=0x01,
    usage=0x05,
    report_ids=(1,),
    in_report_lengths=(6,),
    out_report_lengths=(0,),
)

# Enable the manual gamepad
usb_hid.enable((gamepad,))

print("Manual Gamepad Definition Enabled")
