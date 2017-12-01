#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

FILENAME = "TS33C_samples.dat"

ERROR = 1
INFO = 2
TRACE = 3

class StreamDecoder(object):
    """TS33C Decoder Class"""
    def __init__(self, sample_rate=20000, debug_level=0):
        self.debug_level = debug_level
        self.sample_rate = sample_rate
        self.state = "idle"

        self.chunk_id = 0
        self.pulse_short_limit = 775   # default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.gap_short_limit = 775   #  default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.reset_limit = 2*self.gap_short_limit

        self.currentSymbols = np.empty(0, dtype=np.uint8)
        self.rawBuffer = np.empty(0, dtype=np.uint8)
        self.currentSymbolType = 0
        self.previousSymbolType = 0
        self.temperature = 0
        self.humidity = 0

    def debug(self, message, level=0):
        """Debug output depending on debug level."""
        if self.debug_level >= level:
            print message

    def work(self, input_items):
        """The actual Decoder."""
        rawChunk = input_items[0]
        self.rawBuffer = np.append(self.rawBuffer, rawChunk)

        # we need at least as many samples as is defined by reset_limi
        if self.rawBuffer.size*1e6/self.sample_rate > self.reset_limit:

            # skip empty or zero-only chunks
            if (self.rawBuffer.size > 0) and ((np.sum(self.rawBuffer) > 0) or (self.currentSymbols.size > 0)):

                self.currentSymbolType = self.rawBuffer[0]
                self.debug(("first raw sample", self.rawBuffer[0]), TRACE)
                self.debug(("last raw sample", self.rawBuffer[-1]), TRACE)

                # force edge at beginning an end of rawBuffer
                self.rawBuffer = np.insert(self.rawBuffer, 0, [1 - self.rawBuffer[0]])
                self.rawBuffer = np.append(self.rawBuffer, [1 - self.rawBuffer[-1]])

                self.chunk_id += 1
                self.debug(("Chunk", self.chunk_id), TRACE)
                #self.debug("rawBuffer", rawBuffer.size, rawBuffer)

                # calculate edges from raw data; insert one at beginning for sync
                edges = np.insert(np.diff(self.rawBuffer), 0, [0])
                # position (offset) of edges
                edge_positions = np.ravel(np.nonzero(edges))
                self.debug(("edge_positions:", edge_positions), TRACE)

                self.debug(("edges", edges[np.nonzero(edges)]), TRACE)

                if edge_positions.size > 0:
                    # lengths of pulses and pauses are our symbols, convert to µs
                    symbols = np.diff(edge_positions)*1e6/self.sample_rate

                    # split symbols at packet boundary
                    symbols = np.array(np.split(symbols, np.ravel(np.where(symbols > self.reset_limit))+1))
                    self.debug(("Symbols:", symbols.size, symbols), TRACE)
                    self.debug(("symbols.shape", symbols.shape[0]), TRACE)
                    self.debug(("state", self.state), TRACE)
                    if symbols.shape[0] > 1:
                        self.state = "frame"

                    # process all parts separately
                    for symbol_chunk in symbols:
                        self.debug(("state", self.state), TRACE)
                        if (symbols.size == 1) or self.state == "idle":
                            # skip leading inter-frame gap
                            symbol_chunk = symbol_chunk[1::]
                        if symbol_chunk.size > 0:
                            self.debug(("symbol_chunk:", symbol_chunk.size, symbol_chunk), TRACE)
                            self.state = "frame"

                            # add first symbol to last from previous to reassemble separated pulses/gaps
                            if (self.currentSymbols.size > 0) and (self.previousSymbolType == self.currentSymbolType):
                                self.currentSymbols[-1] += symbol_chunk[0]
                                symbol_chunk = symbol_chunk[1::]

                            self.currentSymbols = np.append(self.currentSymbols, symbol_chunk)

                            if self.currentSymbols[0] > self.reset_limit:
                                self.currentSymbols = self.currentSymbols[1::]

                            self.debug(("currentSymbols:", self.currentSymbols.size, self.currentSymbols), TRACE)

                            # complete packet is determined by long gap at the end
                            if (self.currentSymbols.size > 1) and (self.currentSymbols[-1] > self.reset_limit):

                                # extract pulses
                                pulses = self.currentSymbols[0::2]

                                # extract gaps
                                gaps = self.currentSymbols[1::2]

                                # remove packet pause
                                gaps = np.where(gaps > self.reset_limit, 0, gaps)

                                # calculate histogram to determine length of short and long pulses
                                pulse_histogram = np.histogram(pulses, "auto")

                                # calculate histogram to determine length of short and long gaps; leave out packet pause
                                gap_histogram = np.histogram(gaps[np.where(gaps > 0)], "auto")

                                # derive limits for short pulses/gaps from histogram. Use value in the middle between short and long
                                self.pulse_short_limit = pulse_histogram[1][pulse_histogram[1].size/2]
                                self.gap_short_limit = gap_histogram[1][gap_histogram[1].size/2]

                                self.debug(("Pulses:", pulses.size, pulses), TRACE)
                                self.debug(("Pulse Histogram", pulse_histogram), TRACE)
                                self.debug(("pulse_short_limit", self.pulse_short_limit), TRACE)
                                self.debug(("Gaps:", gaps.size, gaps), TRACE)
                                self.debug(("Gaps Histogram", gap_histogram), TRACE)
                                self.debug(("gap_short_limit", self.gap_short_limit), TRACE)

                                # set short gaps to zero as per decoding rule to remove them later
                                #gaps = np.where(gaps > self.gap_short_limit,gaps,0)

                                # interleave pulses and gaps into one array like this [p, g, p, g, p, g]
                                combined = np.empty(pulses.size + gaps.size, dtype=pulses.dtype)
                                combined[0::2] = pulses
                                combined[1::2] = gaps

                                # remove short gaps
                                #combined = combined[np.where(combined > 0)]
                                self.debug(("combined:", combined.size, combined), TRACE)

                                # convert pulse/gap-width to bits as per decoding rule
                                #rawBits = np.where(combined > self.pulse_short_limit, 0, 1)

                                rawBits = np.empty(combined.size, dtype=np.uint8)
                                self.debug(("rawBits.size", rawBits.size), TRACE)
                                rawBits[0::2] = np.where(combined[0::2] < self.pulse_short_limit, 1, 0)
                                rawBits[1::2] = np.where(combined[1::2] < self.gap_short_limit, 255, 0)

                                # remove short gaps
                                rawBits = rawBits[np.where(rawBits <= 1)]
                                self.debug(("rawBits:", rawBits.size, rawBits), TRACE)

                                # pack raw bits into bytes
                                rawPacket = np.packbits(rawBits)
                                np.set_printoptions(formatter={'int':hex})
                                self.debug(("raw packet:", rawPacket.size, rawPacket), TRACE)
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
                                        packet = np.append(packet, np.uint8(int('{:08b}'.format(item)[::-1], 2)^0xff))

                                    np.set_printoptions(formatter={'int':hex})
                                    self.debug(("packet:", packet.size, packet), INFO)
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
                                        self.temperature = temp/10.
                                        battery_ok = (packet[5]>>6) & 0x01
                                        self.humidity = ((packet[6] & 0xF0) >> 4) * 10 + (packet[6] & 0x0F)

                                        print("Channel:", channel)
                                        print("Rolling Code:", rc)
                                        print("Battery:", battery_ok)
                                        print("Temperature:", self.temperature)
                                        print("Humidity:", self.humidity)
                                    else:
                                        self.debug("Unknown Header", INFO)
                                else:
                                    self.debug("packet too short", INFO)
                                # done with this packet
                                self.currentSymbols = np.empty(0, dtype=np.uint8)
                                #state = "idle"
                            else:
                                self.debug("Waiting for more data", INFO)
                        else:
                            self.debug("skipping empty chunk", INFO)
                            self.state = "idle"
                else:
                    self.debug("no edges in chunk", INFO)
                self.previousSymbolType = self.rawBuffer[-2]
            else:
                #self.debug("Chunk is empty or contains no edges")
                self.state = "idle"
            # all done, delete current rawBuffer
            self.rawBuffer = np.empty(0, dtype=np.uint8)
        else:
            # wait for more samples
            self.debug("filling rawBuffer", INFO)

if __name__ == "__main__":
    decoder = StreamDecoder(debug_level=TRACE)

    rawData = np.ravel(np.fromfile(FILENAME, dtype=np.int8))

    rawStream = np.array_split(rawData, 1000)

    for chunk in rawStream:
        decoder.work([chunk])
