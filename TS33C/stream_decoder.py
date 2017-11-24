#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import struct
import timeit

FILENAME = "TS33C_samples.dat"
SAMPLERATE = 20000  # in Hz

short_limit = 775   # maximum length of a short bit in µs
reset_limit = 2*short_limit

chunk_id = 0

currentSymbols = np.empty(0, dtype=np.uint8)

if __name__ == "__main__":
  rawData = np.ravel(np.fromfile(FILENAME, dtype=np.int8))

  rawStream = np.array_split(rawData, 20)

  for rawChunk in rawStream:
    # skip empty or zero-only chunks    
    if (rawChunk.size > 0) and (np.sum(rawChunk) > 0) :

      print("first raw sample",rawChunk[0])
      print("last raw sample",rawChunk[-1])

      # force edge at beginning an end of rawChunk
      rawChunk = np.insert(rawChunk,0,[1 - rawChunk[0]])
      rawChunk = np.append(rawChunk, [1 - rawChunk[-1]])

      chunk_id += 1
      print("Chunk", chunk_id)

      # calculate edges from raw data; insert one at beginning for sync
      edges = np.insert(np.diff(rawChunk),0,[0])
      # position (offset) of edges
      edge_positions = np.ravel(np.nonzero(edges))
      print("edge_positions:", edge_positions)

      print("edges", edges[np.nonzero(edges)])

      if edge_positions.size > 0:
        # lengths of pulses and pauses are our symbols, convert to µs
        symbols = np.diff(edge_positions)*1e6/SAMPLERATE
        # split symbols at packet boundary
        symbols = np.split(symbols, np.ravel(np.where(symbols>reset_limit))+1)
        print("Symbols:", symbols)

        # process all parts separately
        for symbol_chunk in symbols:
          if symbol_chunk.size > 0:
            print("symbol_chunk:", symbol_chunk.size,symbol_chunk)

            # add first symbol to last from previous to reassemble separated pulses/gaps
            if currentSymbols.size > 0: 
              currentSymbols[-1] += symbol_chunk[0]
              symbol_chunk = symbol_chunk[1::] 

            currentSymbols = np.append(currentSymbols, symbol_chunk)

            print("currentSymbols:", currentSymbols.size,currentSymbols)

            # complete packet is determined by long gap at the end 
            if currentSymbols[-1] > reset_limit:
              # extract pulses
              pulses = currentSymbols[0::2]

              # extract gaps
              gaps = currentSymbols[1::2]

              # set short gaps to zero as per decoding rule to remove them later
              gaps = np.where(gaps>short_limit,gaps,0)

              # remove packet pause
              gaps = np.where(gaps>reset_limit,0,gaps)

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
              rawBits = np.where(combined>short_limit,0,1)
              print("rawBits:", rawBits.size,rawBits)

              # pack raw bits into bytes
              rawPacket = np.packbits(rawBits)
              np.set_printoptions(formatter={'int':hex})
              print("raw packet:", rawPacket.size, rawPacket)
              np.set_printoptions(formatter=None)
              
              if rawPacket.size >= 10:                  
                # prepare final packet
                packet = np.empty(0, dtype=np.uint8)

                # decode all 10 bytes
                for i in range(0, 8):
                  # do some magic
                  item = np.uint8(rawPacket[i+i/8] << (i%8))
                  item |= np.uint8(rawPacket[i+i/8+1] >> (8 - i%8))
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
              # done with this packet
              currentSymbols = np.empty(0, dtype=np.uint8)
            else:
              print("Waiting for more data")
          else:
            print("skipping empty chunk")
      else:
        print("no edges in chunk")
    else:
      print("Chunk is empty or contains no edges")
