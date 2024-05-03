#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decode Symbols"""

from struct import unpack
import numpy as np
from bitarray import bitarray

# raw bits incl. preamble and start/stop bit extracted via inspectrum from a transmission captured via rtl_sdr
sample = bitarray([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0])
# print(sample)

preamble = bitarray("0 11111111 1 0 11001100 1")  # [0xff, 0x33] plus start/stop bits

preamble_start = sample.index(preamble)
print("preamble begins at bit {}".format(preamble_start))
packet = sample[preamble_start:]

#remove start bits
del packet[0:len(packet):10]
#remove stop bits
del packet[8:len(packet):9]

# LSB is sent first, so we need to reverse it here
packet.bytereverse()

# deserialize bits into actual bytes
frame = packet.tobytes()

print("Packet: {}".format(frame.hex(' ')))

# separate message from meta-information
message_length = frame[2] & 0x1f
crc16 = unpack('>H', frame[3 + message_length: 3 + message_length + 2])[0]
message = frame[3:3 + message_length]
print("    Payload Length: {} bytes ({:08b}b) ({} bits)".format(message_length, message_length, message_length * 8))
print("    CRC16: 0x{:04X} ({:08b}b)".format(crc16, crc16))

print("Message: {}".format(message.hex(' ')))
# deserialize message-content
destination, source, payload, counter, mac1, mac2 = unpack('>II{}sHHI'.format(message_length-16),message)
mac = (mac1 << 32) + mac2

print("    Source-Address: 0x{:02X}".format(source))
print("    Target-Address: 0x{:02X}".format(destination))
print("    Payload: {}".format(payload.hex(' ')))
print("    Counter: 0x{:02X} ({})".format(counter, counter))
print("    MAC: 0x{:06X}".format(mac))
