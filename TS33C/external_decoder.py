#!/usr/bin/env python

import numpy as np
import struct

FILENAME = "TS33C_samples.dat"
SAMPLERATE = 20000

#pulse_tolerance = 60
long_limit = 21
short_limit = 11

#long_limit = 200
#short_limit = 130

if __name__ == "__main__":
  rawData = [np.fromfile(FILENAME, dtype=np.byte)]
  if rawData[0].size > 0:
    # to-do
    # - handle high-levels at beginning

    # calculate edges from raw data; insert one at beginning for sync
    edges = np.insert(np.diff(rawData[0]),0,[0])

    # position (offset) of edges
    edge_positions = np.nonzero(edges)
    symbols = np.diff(edge_positions)[0]
    pulses = symbols[0::2]
    gaps = symbols[1::2]

    print("Pulses:", pulses.size,pulses)
    print("Gaps:", gaps.size, gaps)

    # test data
    #pulses = np.array([241, 231, 226, 102, 105, 104, 226, 106, 99, 104, 110, 104, 103, 103, 105, 228, 230, 105, 104, 106, 103, 103, 226, 225, 107, 226, 108, 106, 227, 106, 233, 107, 109, 104, 106, 229, 104, 108, 109, 108, 226, 226, 104, 107, 228, 104, 108, 109, 229, 104, 229, 231, 230, 229, 227, 105, 107, 226, 102, 227, 104, 105, 107, 104, 109, 107, 105])
    #gaps = np.array([257, 261, 143, 140, 261, 140, 139, 145, 139, 137, 259, 143, 141, 138, 140, 258, 138, 139, 141, 139, 265, 139, 264, 260, 139, 138, 258, 141, 259, 134, 136, 137, 139, 260, 137, 140, 138, 134, 137, 260, 264, 140, 137, 261, 260, 138, 135, 137, 261, 139, 257, 258, 259, 262, 138, 138, 262, 142, 263, 139, 138, 139, 261, 136, 136, 138, 2501])
    filtered = np.ravel(np.dstack((pulses,np.where(gaps>long_limit,gaps,0))))
    bits = np.where(filtered[np.where(filtered>0)]>short_limit,0,1)
    packet_raw = np.packbits(bits)
    packet = np.empty(0, dtype=np.uint8)

#    for element in packet_raw.flat:
        #print("0x{:02x}".format(int('{:08b}'.format(element)[::-1], 2)^0xff))
        #print(int('{:08b}'.format(element)[::-1],2)^0xff)
#        packet = np.append(packet, np.uint8(int('{:08b}'.format(element)[::-1],2)^0xff))
        #print(i)
        #print(int('{:08b}'.format(0x06)[::-1], 2)^0xff)

    for i in range(0, 10):
        item = np.uint8(packet_raw[i+i/8] << (i%8))
        item |= np.uint8(packet_raw[i+i/8+1] >> (8 - i%8))
        # reverse and invert bits
        packet = np.append(packet, np.uint8(int('{:08b}'.format(item)[::-1],2)^0xff))

    print("Bits:", bits.size, bits)

    np.set_printoptions(formatter={'int':hex})
    print("raw packet:", packet_raw.size, packet_raw)
    print("packet:", packet.size, packet)

    channel = (packet[1] >> 5) & 0x0F
    if channel >= 5:
        channel -= 1
    rc = packet[1] & 0x0F
    temp = (packet[5] & 0x0F) * 100 + ((packet[4] & 0xF0) >> 4) * 10 + (packet[4] & 0x0F)
    if ((packet[5]>>7) & 0x01) == 0:
        temp = -temp
    battery_ok = (packet[5]>>6) & 0x01
    humidity = ((packet[6] & 0xF0) >> 4) * 10 + (packet[6] & 0x0F)

    print("Channel:", channel)
    print("Rolling Code:", rc)
    print("Battery:", battery_ok)
    print("Temperature:", temp/10.)
    print("Humidity:", humidity)

    #print(np.histogram(pulses, bins=[0,11,21,80,10000]))
