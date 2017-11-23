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
  rawData = np.ravel(np.fromfile(FILENAME, dtype=np.uint8))

  rawStream = np.array_split(rawData, 1)

  for rawChunk in rawStream:
    if rawChunk.size > 0:
      # FIXME: handle high-levels at beginning of rawData
      #print(rawChunk)

      # calculate edges from raw data; insert one at beginning for sync
      edges = np.insert(np.diff(rawChunk),0,[0])
      # position (offset) of edges
      edge_positions = np.ravel(np.nonzero(edges))
      #print("edge_positions:", edge_positions)

      if edge_positions.size > 0:
        # lengths of pulses and pauses are our symbols
        symbols = np.diff(edge_positions)
        # extract pulses and convert to µs
        pulses = symbols[0::2]*1e6/SAMPLERATE
        print(np.histogram(pulses, bins=[0,short_limit,2*short_limit,100000]))

        # extract gaps; add long gap at the end for symmetry with pulses
        gaps = np.append(symbols[1::2],np.amax(symbols))*1e6/SAMPLERATE

        #print(np.histogram(gaps, bins=[0,short_limit,2*short_limit,100000]))

        # set short gaps to zero as per decoding rule to remove them later
        # convert to µs
        gaps = np.where(gaps>short_limit,gaps,0)

        print("Pulses:", pulses.size,pulses)
        print("Gaps:", gaps.size, gaps)

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

        # FIXME: decode multiple packets as well
        for i in range(0, 10):
          # do some magic
          item = np.uint8(packet_raw[i+i/8] << (i%8))
          item |= np.uint8(packet_raw[i+i/8+1] >> (8 - i%8))
          # reverse and invert bits; add to packet
          packet = np.append(packet, np.uint8(int('{:08b}'.format(item)[::-1],2)^0xff))

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
      else:
        print("no edges in chunk")
    else:
      print("Chunk is empty")
