#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Live decoder for TFA Dostmann Thermo-Hygro Sensor 30.3180.IT"""

import numpy as np

FILENAME = "303180IT_bits.dat"

ERROR = 1
INFO = 2
TRACE = 3

class StreamDecoder(object):
    """30.3180.IT Decoder Class"""
    # pylint: disable=too-many-instance-attributes, C0301, C0103

    def __init__(self, sample_rate=20000, debug_level=0):
        self.debug_level = debug_level
        self.sample_rate = sample_rate
        self.state = "idle"

        self.chunk_id = 0
        self.pulse_short_limit = 30   # default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.gap_short_limit = 30   #  default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.reset_limit = 500

        self.currentSymbols = np.empty(0, dtype=np.uint8)
        self.rawBuffer = np.empty(0, dtype=np.uint8)
        self.currentSymbolType = 0
        self.previousSymbolType = 0

        # sensor data
        self.identifier = 0
        self.temperature = 0
        self.humidity = 0
        self.battery_ok = False


    def debug(self, message, level=0):
        """Debug output depending on debug level."""
        if self.debug_level >= level:
            print message

    @classmethod
    def crc8(cls, data):
        """Simple CRC-8 calculator"""
        generator = 0x31    # x^8 + x^5 + x^4 + 1
        crc = np.uint8(0)   # use uint8

        for currByte in data:
            crc ^= currByte
            for i in range(8):
                if (crc & 0x80) != 0:
                    crc = np.uint8((crc << 1) ^ generator)
                else:
                    crc <<= 1
        return crc

    def work(self, input_items):
        """The actual Decoder."""
        # pylint: disable=too-many-nested-blocks, too-many-statements, R0914, R0912, C0301

        rawChunk = input_items[0]
        self.rawBuffer = np.append(self.rawBuffer, rawChunk)

        # we need at least as many samples as is defined by reset_limit
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

                    # if symbols are split into 2+ arrays at packet boundary we
                    # have a valid frame
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

                                # remove first few symbols
                                self.currentSymbols = self.currentSymbols[6:]

                                # sync pattern - about 75 bits
                                sync = self.currentSymbols[:2*75]
                                symbol_length = np.mean(np.sum(np.reshape(sync, (-1, 2)), axis=1))
                                baudrate = int(1e6/symbol_length)
                                self.debug(("symbol_length:", symbol_length), TRACE)
                                self.debug(("baudrate:", baudrate), TRACE)

                                # determine start of data packet
                                data_start = np.where(self.currentSymbols > symbol_length*1.5)[0][0]
                                self.debug(("data_start:", data_start), TRACE)

                                # extract pulses
                                pulses = self.currentSymbols[data_start:-1:2]

                                # remove short pulses (they are just part of zeroes)
                                pulses = np.where(pulses < symbol_length, 0, pulses)

                                # extract gaps
                                gaps = self.currentSymbols[data_start+1:-1:2]

                                self.debug(("Pulses:", pulses.size, pulses), TRACE)
                                self.debug(("Gaps:", gaps.size, gaps), TRACE)

                                # interleave pulses and gaps into one array like this [p, g, p, g, p, g]
                                combined = np.empty(pulses.size + gaps.size, dtype=pulses.dtype)
                                combined[0::2] = np.floor(pulses/symbol_length)
                                combined[1::2] = np.ceil(gaps/symbol_length)

                                self.debug(("combined:", combined.size, combined), TRACE)

                                # FIXME - there must be a more elegant solution...
                                rawBits = np.empty(0, dtype=np.uint8)
                                for index, symbol in np.ndenumerate(combined):
                                    if symbol:
                                        if not index[0] % 2:
                                            rawBits = np.append(rawBits, np.ones(int(symbol), dtype=np.uint8))
                                        else:
                                            rawBits = np.append(rawBits, np.zeros(int(symbol), dtype=np.uint8))

                                self.debug(("rawBits:", rawBits.size, rawBits), TRACE)

                                # make sure we have at least 11 bytes
                                if rawBits.size >= 11*8:
                                    # use the first eleven bytes only, swap MSB and LSB, pack 8 bits into one byte, reverse order to compensate for 1st flip
                                    packet = np.packbits(rawBits[:11*8][::-1])[::-1]

                                    # check CRC8
                                    if self.crc8(packet[2:10]) == packet[10]:
                                        np.set_printoptions(formatter={'int':hex})
                                        self.debug(("packet:", packet.size, packet), INFO)
                                        np.set_printoptions(formatter=None)

                                        self.identifier = "{:02X}".format((packet[2]<<8) + packet[3])
                                        self.temperature = (packet[4] & 0x0f) * 10 + ((packet[5]>>4) & 0x0f) * 1 + (packet[5] & 0x0f) * 0.1 - 40
                                        self.humidity = (packet[6] & 0x7f)
                                        self.battery_ok = (packet[7]>>7) & 0x01 == 0

                                        self.debug(("Identifier:", self.identifier), INFO)
                                        self.debug(("Battery ok:", self.battery_ok), INFO)
                                        print "Temperature: %02.1f°C" % self.temperature
                                        print "Humidity: %02i%%" % self.humidity
                                    else:
                                        self.debug("CRC-Check failed", ERROR)
                                else:
                                    self.debug("Invalid packet length", ERROR)

                                # done with this packet
                                self.currentSymbols = np.empty(0, dtype=np.uint8)
                            else:
                                self.debug("Waiting for more data", TRACE)
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
            self.debug("filling rawBuffer", TRACE)

def main():
    """ main function """
    # set up decoder
    decoder = StreamDecoder(sample_rate=2000000, debug_level=TRACE)

    # load raw binary data from file
    raw_data = np.ravel(np.fromfile(FILENAME, dtype=np.int8))

    # simulate streaming of input data
    raw_stream = np.array_split(raw_data, 200)
    #raw_stream = [raw_data]

    for chunk in raw_stream:
        # feed chunks to decoder
        decoder.work([chunk])

if __name__ == "__main__":
    main()
