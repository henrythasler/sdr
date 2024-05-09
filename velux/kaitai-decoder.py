#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decode Symbols using auto-generated code"""

# pip install crc kaitaistruct
from crc import Calculator, Crc16
from iohomecontrol import Iohomecontrol as iohc, KaitaiStream, BytesIO

packet = bytes([0xff, 0x33, 0xf6, 0x20, 0x00, 0x00, 0x3f, 0xda, 0x2c, 0x93, 0x00, 0x01, 0x61, 0xd2, 0x00, 0x00, 0x00, 0x04, 0x76, 0x23, 0x14, 0x50, 0x08, 0x11, 0x50, 0x2d, 0x15])
decoded = iohc(KaitaiStream(BytesIO(packet)))

print("Control 1:")
print("    Order: {}".format(decoded.control1.order))
print("    Mode: {}".format(decoded.control1.mode))
print("    Payload Length: {}".format(decoded.control1.payload_length))
print("Control 2:")
print("    use_beacon: {}".format(decoded.control2.use_beacon))
print("    routed: {}".format(decoded.control2.routed))
print("    low_power_mode: {}".format(decoded.control2.low_power_mode))
print("    ack: {}".format(decoded.control2.ack))
print("    protocol_version: {}".format(decoded.control2.protocol_version))
print("Source Node-ID: 0x{:06x}".format(decoded.source_id))
print("Target Node-ID: 0x{:06x}".format(decoded.target_id))
print("Command: {}".format(decoded.command))
print("Payload: {}".format(decoded.parameter.hex(" ")))
print("Counter: 0x{:04x} ({})".format(decoded.counter, decoded.counter))
print("MAC: {}".format(decoded.mac.hex(" ")))

crc_ok = Calculator(Crc16.KERMIT).verify(packet[2:-2], decoded.checksum)
print("Checksum: {} (0x{:04x})".format("OK" if crc_ok else "Error", decoded.checksum))
