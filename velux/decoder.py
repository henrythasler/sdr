#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decode Symbols"""

from struct import unpack
import numpy as np

# raw bits incl. preamble and start/stop bit extracted via inspectrum from a transmission captured via rtl_sdr
packet = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0]
packet_str = ''.join(str(x) for x in packet)

# 
preamble_bytes = [0xff, 0x33]
preamble_end_pattern = f'0{preamble_bytes[0]:0<8b}10{preamble_bytes[1]:0<8b}1'  # https://www.pythonmorsels.com/string-formatting/
preamble_end = packet_str.find(preamble_end_pattern)
print("preamble ends at bit {}".format(preamble_end))

# strip start and stop bits
raw = np.array(packet[preamble_end + len(preamble_end_pattern):], dtype=np.uint8)
print(raw[0:32])
#print(np.arange(0, np.shape(raw)[0], 9))
#print(np.arange(8, np.shape(raw)[0], 8))
raw = np.delete(raw, np.arange(0, np.shape(raw)[0], 10))
print(raw[0:32])
raw = np.delete(raw, np.arange(8, np.shape(raw)[0], 9))
print(raw[0:32])

print(raw[0:8])
print(raw[7::-1])
payload_length = np.packbits(raw[7::-1])[0] & 0x1f     #  10110=22
print("payload_length={} ({:08b}b) ({} bits)".format(payload_length, payload_length, payload_length * 8))

print(np.shape(raw))

crc16 = np.packbits(raw[8+payload_length+16:8+payload_length:-1])[0]
print(crc16)

#raw = raw[].reshape((-1, 8))
#print(raw)

# message = 