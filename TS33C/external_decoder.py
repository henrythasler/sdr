#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import struct
import timeit

FILENAME = "TS33C_samples.dat"
SAMPLERATE = 20000  # in Hz

short_limit = 775   # maximum length of a short bit in µs
reset_limit = 2*short_limit

#long_limit = 200
#short_limit = 130

if __name__ == "__main__":
  rawData = [np.fromfile(FILENAME, dtype=np.byte)]
  if rawData[0].size > 0:
    # FIXME: handle high-levels at beginning of rawData

    # calculate edges from raw data; insert one at beginning for sync
    edges = np.insert(np.diff(rawData[0]),0,[0])

    # position (offset) of edges
    edge_positions = np.ravel(np.nonzero(edges))
    #print("edge_positions:", edge_positions)

    # lengths of pulses and pauses are our symbols, convert to µs
    symbols = np.diff(edge_positions)*1e6/SAMPLERATE
    print("symbols", symbols.size, symbols)

    # extract pulses
    pulses = symbols[0::2]
    print(np.histogram(pulses, bins=[0,short_limit,2*short_limit,100000]))

    # extract gaps; add long gap at the end for symmetry with pulses
    gaps = np.append(symbols[1::2],np.amax(symbols))*1e6/SAMPLERATE
    print(np.histogram(gaps, bins=[0,short_limit,2*short_limit,100000]))
    # set short gaps to zero as per decoding rule to remove them later
    # convert to µs
    gaps = np.where(gaps>short_limit,gaps,0)

    print("Pulses:", pulses.size,pulses)
    print("Gaps:", gaps.size, gaps)

    # test data
    #pulses = np.array([241, 231, 226, 102, 105, 104, 226, 106, 99, 104, 110, 104, 103, 103, 105, 228, 230, 105, 104, 106, 103, 103, 226, 225, 107, 226, 108, 106, 227, 106, 233, 107, 109, 104, 106, 229, 104, 108, 109, 108, 226, 226, 104, 107, 228, 104, 108, 109, 229, 104, 229, 231, 230, 229, 227, 105, 107, 226, 102, 227, 104, 105, 107, 104, 109, 107, 105])
    #gaps = np.array([257, 261, 143, 140, 261, 140, 139, 145, 139, 137, 259, 143, 141, 138, 140, 258, 138, 139, 141, 139, 265, 139, 264, 260, 139, 138, 258, 141, 259, 134, 136, 137, 139, 260, 137, 140, 138, 134, 137, 260, 264, 140, 137, 261, 260, 138, 135, 137, 261, 139, 257, 258, 259, 262, 138, 138, 262, 142, 263, 139, 138, 139, 261, 136, 136, 138, 2501])

    # combine pulses and gaps into one array like this [p, g, p, g, p, g]
    combined = np.ravel(np.dstack((pulses,gaps)))
    # remove short gaps
    combined = combined[np.where(combined>0)]
    print("combined:", combined.size,combined)

    # convert pulse/gap-width to bits as per decoding rule
    raw_bits = np.where(combined>short_limit,0,1)

    # pack raw bits into bytes
    packet_raw = np.packbits(raw_bits)

    # prepare final packet
    packet = np.empty(0, dtype=np.uint8)

#    for element in packet_raw.flat:
        #print("0x{:02x}".format(int('{:08b}'.format(element)[::-1], 2)^0xff))
        #print(int('{:08b}'.format(element)[::-1],2)^0xff)
#        packet = np.append(packet, np.uint8(int('{:08b}'.format(element)[::-1],2)^0xff))
        #print(i)
        #print(int('{:08b}'.format(0x06)[::-1], 2)^0xff)

    #start_time = timeit.default_timer()

    # FIXME: decode multiple packets as well
    for i in range(0, 10):
        # do some magic
        item = np.uint8(packet_raw[i+i/8] << (i%8))
        item |= np.uint8(packet_raw[i+i/8+1] >> (8 - i%8))
        # reverse and invert bits; add to packet
        packet = np.append(packet, np.uint8(int('{:08b}'.format(item)[::-1],2)^0xff))
        #packet = np.append(packet, item)

    # switch MSB and LSB
    #packet = np.packbits(np.ravel(np.asarray(np.hsplit(np.unpackbits(packet), np.arange(8,np.unpackbits(packet).size,8)))[:,::-1]))
    # invert bits
    #packet ^= 0xFF
    #elapsed = timeit.default_timer() - start_time
    #print(elapsed)

    np.set_printoptions(formatter={'int':hex})
    print("raw packet:", packet_raw.size, packet_raw)
    print("packet:", packet.size, packet)

    # check for correct header-byte
    if packet[0] == 0x9f:
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
    else:
        print("Unknown Header")
