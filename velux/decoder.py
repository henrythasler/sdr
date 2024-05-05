#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decode Symbols"""

"""
pip install crc bitarray
"""

# from struct import unpack
import numpy as np

# from bitarray import bitarray
from crc import Calculator, Crc16
import bitstring

"""
terminology according to https://dev.to/stungnet/from-data-to-frame-the-evolution-of-pdus-across-the-osi-model-21gd
"""


# raw bits incl. preamble, SOF and start/stop bit extracted via inspectrum from a transmission captured via rtl_sdr
# bits = bitarray([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0])

"""
f6 00 00 00 3f da 2c 93 00 01 61 d2 00 00 00 04 76 23 14 50 08 11 50 c8 97
Dest ID   : 3f000000     Msg type  : f6            Message   : 0161d2000000  Counter   : 1142          MAC       : 231450081150
"""
bits = bitstring.Bits([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1])

# need to find the frame within raw input bits
frame_start = bits.find(bitstring.Bits(bin="0 11111111 1 0 11001100 1".replace(" ", ""))) # [0xff, 0x33] plus start/stop bits

if not frame_start:
    exit()

frame_start = frame_start[0]

print("Received {} bits. Frame begins at bit {}".format(len(bits), frame_start))
frame = bitstring.BitArray(bits[frame_start:])

# remove start bits
del frame[0 : len(frame) : 10]
# remove stop bits
del frame[8 : len(frame) : 9]

# LSB is sent first for each byte, so we need to reverse it here
for i in range(0, len(frame) - 8, 8):
    frame.reverse(i, i + 8)

# by now it's a packet
packet = frame
print("\r\nPacket: {}".format(packet.tobytes().hex(" ")))

# separate message from meta-information
_, control1, _ = packet.unpack("uint:16, uint:8, bin")
payload_length = control1 & 0x1F

_, crc16 = packet.unpack("bytes:{}, uintle:16".format(3 + payload_length))
crc_calc = Calculator(Crc16.KERMIT).checksum(packet.tobytes()[2 : 3 + payload_length])
payload = packet[3 * 8 : 3 * 8 + payload_length * 8]    # strip SFD and control1
print(
    "    Payload Length: {} bytes (0x{:02X}, {:08b}b), {} bits)".format(
        payload_length, payload_length, payload_length, payload_length * 8
    )
)
print(
    "    CRC16: {} (0x{:04X})".format(
        (
            "OK"
            if crc_calc == crc16
            else "ERROR, expected 0x{:04X} but received".format(crc_calc)
        ),
        crc16,
    )
)

print("\r\nMessage: {}".format(payload.tobytes().hex(" ")))
# deserialize message-content
control2, destination, source, command, payload, counter, mac = payload.unpack(
    "uint:8, uint:24, uint:24, uint:8, bytes:{}, uint:16, uint:48".format(
        payload_length - 16
    )
)

print("    Control1: 0x{:02X} (0b{:08b})".format(control1 & ~0x1f, control1 & ~0x1f))
print("    Control2: 0x{:02X} (0b{:08b})".format(control2, control2))
print("    Source Node-ID: 0x{:06X}".format(source))
print("    Target Node-ID: 0x{:06X}".format(destination))
print("    Command: 0x{:02X}".format(command))
print("    Payload: {}".format(payload.hex(" ")))
print("    Counter: 0x{:04X} ({})".format(counter, counter))
print("    MAC: 0x{:012X}".format(mac))
