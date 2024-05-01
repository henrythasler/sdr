#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decode Symbols"""

from struct import unpack
import numpy as np

""" 
if you have just the amplitude values
"""
symbols = np.array([-0.978973, 1.17879, 2.16441, -0.967268, -0.982979, 1.37306, 2.51, -0.999145, 1.4218, -0.954867, 2.83086, -0.969731, 1.15073, -0.983953, 3.25464, -0.998677, 1.11787, -0.99313, 3.25513, -0.989338, -0.978772, 2.40098, 3.29982, -0.984729, 1.50293, -0.986528, -0.963995, 1.20755, 1.59645, -0.99533, -0.985346, 1.18317, 1.64338, -0.995102, 2.13389, -0.982879, -0.993841, 3.24691, -0.992873, 1.20331, 2.66343, -0.952425, -0.987252, 1.20161, 2.59331, -0.969275, 1.38687, -0.997695, 2.98722, -0.9972, -0.998467, 1.6104, -0.963154, 2.09193, -0.930562, 1.8342, 3.27179, -0.999958, -0.984508, 1.88797, 3.37359, -0.942826, 1.2013, -0.943561, -0.933611, 1.35861, 1.24165, -0.998798, -0.990742, 1.35632, -0.999038, 3.02884, 2.40309, -0.997628, -0.935958, 3.30769, 2.30419, -0.9832, 1.63471, -0.975439, -0.948221, 1.15124, -0.984419, 3.24191, -0.977503, 1.12283, 2.38821, -0.975889, -0.978687, 1.41261, 2.46522, -0.985991, -0.999118, 1.39793, -0.972895, 2.56144, -0.951851, 1.53168, -0.971966, 2.53196, 1.16685, -0.965457, -0.998545, 1.80703, -0.996224, 2.01978, -0.99918, 2.01255, 1.12455, -0.96652, -0.960314, 1.72671])
convert_symbols = np.vectorize(lambda x: 1 if x > 0 else 0)
manchester = convert_symbols(symbols)


"""
stop-command with custom transmitter

$ sudo python3 transmitter.py stop
key: 0xA0, ctrl: 0x01, rolling code: 0x05, address: 0x365240
cksum: 13
Data: 0xA5 0x1D 0x00 0x05 0x40 0x52 0x36 
Frame: 0xA5 0xB8 0xB8 0xBD 0xFD 0xAF 0x99

extract 112 manchester encoded half-symbols via inspectrum
"""
manchester = np.array([0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1])
bits = np.ravel(np.where(np.reshape(manchester, (-1, 2)) == [0, 1], 1, 0))[::2]

print("Bits: {} ({})".format(len(bits), bits))
payload = np.packbits(bits)
print("Payload: "+''.join('0x{:02X} '.format(x) for x in payload))

frame = np.zeros(7, dtype=np.uint8)
# de-obfuscation
frame[0] = payload[0]
for i in range(1, 7):
    frame[i] = payload[i] ^ payload[i-1]

#print("Frame: "+''.join('0x{:02X} '.format(x) for x in frame))

# checksum calculation
cksum = 0
for i in range(0,7):
    cksum = cksum ^ frame[i] ^ (frame[i] >> 4)
cksum = cksum & 0xf

COMMANDS={
    0x00: 'null',
    0x01: 'stop',
    0x02: 'up',
    0x04: 'down',
    0x08: 'prog',
    }

rolling_code = unpack(">H", frame[2:4])[0]
address = unpack("<I", frame[4:7].tobytes() + b"\x00")[0]
control = (frame[1] >> 4) & 0x0f

print("Frame: "+''.join('0x{:02X} '.format(x) for x in frame))
print("    Checksum: {}".format("ok" if cksum==0 else "error"))
print("    Key: 0x{:02X}".format(frame[0]))
print("    Control: {} (0x{:02X})".format(COMMANDS[control], control))
print("    Rolling Code: {} (0x{})".format(rolling_code, ''.join('{:02X}'.format(x) for x in frame[2:4])))
print("    Address: {} (0x{})".format(address, ''.join('{:02X}'.format(x) for x in frame[7:3:-1])))
