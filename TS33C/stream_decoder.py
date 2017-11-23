#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import struct
import timeit

FILENAME = "TS33C_samples.dat"
SAMPLERATE = 20000  # in Hz

short_limit = 775   # maximum length of a short bit in µs
reset_limit = 2*short_limit

state = "idle" # or "packet"
chunk_id = 0

if __name__ == "__main__":
  rawData = np.ravel(np.fromfile(FILENAME, dtype=np.int8))

  rawStream = np.array_split(rawData, 10)

  for rawChunk in rawStream:
    if rawChunk.size > 0:
      # FIXME: handle high-levels at beginning of rawData
      #print(rawChunk)
      chunk_id += 1
      print("Chunk", chunk_id)

      # calculate edges from raw data; insert one at beginning for sync
      edges = np.insert(np.diff(rawChunk),0,[0])
      # position (offset) of edges
      edge_positions = np.ravel(np.nonzero(edges))
      #print("edge_positions:", edge_positions)

      print("edges", edges[np.nonzero(edges)])

      if edge_positions.size > 0:
        # lengths of pulses and pauses are our symbols
        symbols = np.diff(edge_positions)
        print("Symbols:", symbols.size, symbols)

        # extract pulses, convert to µs
        pulses = symbols[0::2]*1e6/SAMPLERATE

        # extract gaps, convert to µs
        gaps = symbols[1::2]*1e6/SAMPLERATE

        # set short gaps to zero as per decoding rule to remove them later
        gaps = np.where(gaps>short_limit,gaps,0)

        print("Pulses:", pulses.size,pulses)
        print("Gaps:", gaps.size, gaps)

        # interleave pulses and gaps into one array like this [p, g, p, g, p, g]
        combined = np.empty(pulses.size + gaps.size, dtype=pulses.dtype)
        combined[0::2] = pulses
        combined[1::2] = gaps

        # remove short gaps
        combined = combined[np.where(combined>0)]
        print("combined:", combined.size,combined)

        # convert pulse/gap-width to bits as per decoding rule
        raw_bits = np.where(combined>short_limit,0,1)
        print("raw_bits:", raw_bits.size,raw_bits)

        # pack raw bits into bytes
        packet_raw = np.packbits(raw_bits)
        np.set_printoptions(formatter={'int':hex})
        print("raw packet:", packet_raw.size, packet_raw)
        np.set_printoptions(formatter=None)

        if packet_raw.size >= 10:
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
          print("packet:", packet.size, packet)
          np.set_printoptions(formatter=None)

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
          print("packet too short")
      else:
        print("no edges in chunk")
    else:
      print("Chunk is empty")
