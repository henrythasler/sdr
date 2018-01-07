#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Decoder for Hideki TS33C Wireless Temperature/Humidity Sensor
    for Raspberry Pi with RXB8 Receiver
"""
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import os
import pigpio as gpio
import numpy as np

from time import sleep, time
from datetime import datetime

# used for further processing of received data
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import json

SILENT = 0
ERROR = 1
INFO = 2
TRACE = 3

class RXB8_Decoder(object):
    """Decoder-Class for external Receiver"""
    def __init__(self, host="localhost", port=8888, debug_level=SILENT):
        self.debug_level = debug_level
        self.host = host
        self.port = port
        self.onDecode = None

        # set up pigpio connection
        self.pi = gpio.pi(self.host, self.port)
        if not self.pi.connected:
            self.debug("Could not connected to " + self.host)
            exit()
        self.callback = None

        # initialize timestamp for further use
        self.start_tick = self.pi.get_current_tick()

        # control variables
        self.active = False     # enables the decoder 

        # symbol parameters
        self.pulse_short_limit = 775   # default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.gap_short_limit = 775   #  default value for maximum length of a short bit in µs (valid for optimal rx quality)
        self.frame_gap = 4*self.gap_short_limit

        # receiver data
        self.edges = np.empty(0, dtype=np.uint8)
        self.edge_positions = np.empty(0, dtype=np.uint32)

        # decoding variables
        self.state = "idle"
        self.currentSymbols = np.empty(0, dtype=np.uint8)
        self.min_edges = 120

        # sensor data
        self.temperature = 0
        self.humidity = 0

    def __enter__(self):
        """Class can be used in with-statement"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """clean up stuff"""
        if self.callback:
            self.callback.cancel()
        self.pi.stop()

    def debug(self, message, level=0):
        """Debug output depending on debug level."""
        if self.debug_level >= level:
            print message

    def write_png(self, filename, data, title=None):
        fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
        fig.set_size_inches(16, 3)
        ax.set_title(title, fontsize=10)
        fig.text(0.5, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fontsize=8, color='black',
            ha='center', va='bottom', alpha=0.4)
        ax.step(data[0], data[1], linewidth=1, where='post')
        ax.grid(True)
        plt.tight_layout()
        fig.savefig(filename)
        plt.close(fig)    # close the figure          

    def cbf(self, pin, level, tick):
        if level < 2:
            if self.start_tick < tick:
                self.edge_positions = np.append(self.edge_positions, gpio.tickDiff(self.start_tick, tick))
                self.edges = np.append(self.edges, level)
        # watchdog event
        else:
#            self.debug("reset gap detected")
            self.edge_positions = np.append(self.edge_positions, gpio.tickDiff(self.start_tick, tick))

            # marker for watchdog
            self.edges = np.append(self.edges, 4)
            self.decode()

    def decode(self):
        # set semaphore
        self.decoding = True

        # check for at least 130 edges
        if self.edge_positions.size > self.min_edges and self.active:
            self.debug(("edge_positions:", self.edge_positions.size, self.edge_positions), TRACE)
            self.debug(("edges", self.edges.size, self.edges), TRACE)
            self.debug(("frame_gap:", self.frame_gap), TRACE)

            # lengths of pulses and pauses are our symbols, convert to µs
            symbols = np.diff(self.edge_positions)

            # split symbols at packet boundary
            symbols = np.array(np.split(symbols, np.ravel(np.where(symbols > self.frame_gap))+1))

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

                    """
                    if (self.currentSymbols.size > 0) and (self.previousSymbolType == self.currentSymbolType):
                        self.currentSymbols[-1] += symbol_chunk[0]
                        symbol_chunk = symbol_chunk[1::]
                    """
                    
                    self.currentSymbols = np.append(self.currentSymbols, symbol_chunk)

                    if self.currentSymbols[0] > self.frame_gap:
                        self.currentSymbols = self.currentSymbols[1::]

                    self.debug(("currentSymbols:", self.currentSymbols.size, self.currentSymbols), TRACE)

                    # complete packet is determined by long gap at the end
                    if (self.currentSymbols.size > 1) and (self.currentSymbols[-1] > self.frame_gap):

                        # extract pulses
                        pulses = self.currentSymbols[0::2]

                        # extract gaps
                        gaps = self.currentSymbols[1::2]

                        # remove packet pause
                        gaps = np.where(gaps > self.frame_gap, 0, gaps)

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

                        # interleave pulses and gaps into one array like this [p, g, p, g, p, g]
                        combined = np.empty(pulses.size + gaps.size, dtype=pulses.dtype)
                        combined[0::2] = pulses
                        combined[1::2] = gaps

                        self.debug(("combined:", combined.size, combined), TRACE)

                        # convert pulse/gap-width to bits as per decoding rule
                        rawBits = np.empty(combined.size, dtype=np.uint8)
                        self.debug(("rawBits.size", rawBits.size), TRACE)
                        rawBits[0::2] = np.where(combined[0::2] < self.pulse_short_limit, 1, 0)
                        rawBits[1::2] = np.where(combined[1::2] < self.gap_short_limit, 255, 0)

                        # remove short gaps marked as 255 above
                        rawBits = rawBits[np.where(rawBits <= 1)]
                        self.debug(("rawBits:", rawBits.size, rawBits), TRACE)

                        # prepare boolean mask for parity bits (every 9th bit)
                        parityMask = np.mod(np.arange(rawBits.size)+1, 9) == 0

                        # extract parity bits as boolean array
                        parityBits = np.extract(parityMask, rawBits) == 1
                        # extract packet bits as boolean array
                        packetBits = np.extract(np.invert(parityMask), rawBits) == 1

                        # make sure we have whole bytes (8 bit)
                        if (packetBits.size % 8) == 0:
                            # swap MSB and LSB, invert Bits, pack 8 bits into one byte, reverse order to compensate for 1st flip
                            packet = np.packbits(np.invert(packetBits[::-1]))[::-1]

                            np.set_printoptions(formatter={'int':hex})
                            self.debug(("packet:", packet.size, packet), INFO)
                            # calculate parity of each byte by splitting the bits into reversed and inverted 8-bit parts and
                            # calculate the sum of set bits;
                            packetParity = (np.sum(np.split(np.invert(packetBits[::-1]), np.arange(8, packetBits.size, 8)), axis=1)[::-1] % 2) == 0

                            self.debug(("packetParity:", packetParity.size, packetParity), TRACE)
                            np.set_printoptions(formatter=None)

                            # check parity of packet
                            if np.array_equal(packetParity, parityBits):
                                # check for correct sensor type and header-byte
                                if (packet.size == 10) and (packet[0] == 0x9f):
                                    #extract values from packet
                                    channel = (packet[1] >> 5) & 0x0F
                                    if channel >= 5:
                                        channel -= 1
                                    rollingCode = packet[1] & 0x0F
                                    temp = (packet[5] & 0x0F) * 100 + ((packet[4] & 0xF0) >> 4) * 10 + (packet[4] & 0x0F)
                                    sign = (((packet[5]>>7) & 0x01) * 2) - 1
                                    self.temperature = temp*sign/10.
                                    battery_ok = (packet[5]>>6) & 0x01 == 1
                                    self.humidity = ((packet[6] & 0xF0) >> 4) * 10 + (packet[6] & 0x0F)

                                    self.debug(("Channel:", channel), INFO)
                                    self.debug(("Rolling Code:", rollingCode), INFO)
                                    self.debug(("Battery ok:", battery_ok), INFO)
                                    self.debug("Temperature: %02.1f°C" % self.temperature, INFO)
                                    self.debug("Humidity: %02i%%" % self.humidity, INFO)

                                    # create plot of current packet
                                    #self.write_png('pass_{}.png'.format(self.start_tick), [self.edge_positions/1000., self.edges], u"Temp={}, Hum={}".format(self.temperature, self.humidity))

                                    if self.onDecode:
                                        self.onDecode(json.dumps({'timestamp': int(time()), 'value': self.temperature, 'unit': '°C'}))
                                    #self.active = False
                                else:
                                    self.debug("Unknown Sensor or Header", ERROR)
                            else:
                                self.debug("Parity check failed", ERROR)
                                self.write_png('parity_error_{}.png'.format(self.start_tick), [self.edge_positions/1000., self.edges], u"parity error")
                                
                        else:
                            self.debug("Invalid packet length", ERROR)
                            self.write_png('packet_length_{}.png'.format(self.start_tick), [self.edge_positions/1000., self.edges], u"Invalid packet length")
                        # done with this packet
                        self.currentSymbols = np.empty(0, dtype=np.uint8)
                    else:
                        self.debug("Waiting for more data", TRACE)
                else:
                    self.debug("skipping empty chunk", INFO)
                    self.state = "idle"
        else:
            #self.debug("discarding invalid rf data", TRACE)
            pass
            
        # reset buffer
        self.start_tick = self.pi.get_current_tick()
        self.edges = np.empty(0, dtype=np.uint8)
        self.edge_positions = np.empty(0, dtype=np.uint32)

    def run(self, pin=17, glitch_filter=150, frame_gap=3100, onDecode=None):
        # callback after successful decode
        self.onDecode=onDecode

        # filter high frequency noise
        self.pi.set_glitch_filter(pin, glitch_filter)

        # set timespan (in µs) between frames
        self.frame_gap = frame_gap

        # detect frame gap to try decoding of received data
        self.pi.set_watchdog(pin, int(self.frame_gap/1000))
        # watch pin
        self.callback = self.pi.callback(pin, gpio.EITHER_EDGE, self.cbf)

        # wait for something to happen
        self.active = True
        while self.active:
            sleep(.1)

class Mqtt(object):
    def __init__(self, host="localhost", debug_level=SILENT):
        self.debug_level = debug_level
        self.host = host
        self.connected = False

        self.client = mqtt.Client('rxb8-%s' % os.getpid())
        self.client.on_connect = self.on_connect

        self.client.connect(self.host)
        self.client.loop_start()

    def __enter__(self):
        """Class can be used in with-statement"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.loop_stop()
        self.client.disconnect()

    def debug(self, message, level=0):
        """Debug output depending on debug level."""
        if self.debug_level >= level:
            print message

    def publish(self, json_data):
        if self.connected:
            self.client.publish("home/test/rxb8", json_data, retain=False)

    def on_connect(self, client, userdata, flags, rc):
        self.debug(("Connected to mqtt broker:", self.host), TRACE)
        self.connected = True

def main():
    """ main function """
    # set up decoder
    with RXB8_Decoder(host="rfpi", debug_level=INFO) as decoder:
        with Mqtt(host="osmc", debug_level=SILENT) as client:
            try:
                decoder.run(pin=17, glitch_filter=150, frame_gap=20000, onDecode=client.publish)
            except KeyboardInterrupt:
                print "cancel"

if __name__ == "__main__":
    main()