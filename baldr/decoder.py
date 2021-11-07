#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from time import sleep, time
from datetime import datetime

import pigpio as gpio
import numpy as np

from lib.rfm69 import Rfm69

import paho.mqtt.client as mqtt

SILENT = 0
ERROR = 1
INFO = 2
TRACE = 3


class Decoder(object):
    """Decoder-Class for external Receiver"""
    def __init__(self, host="localhost", port=8888, data_pin=25, reset_pin=24, pi=None, debug_level=SILENT):
        self.debug_level = debug_level
        self.host = host
        self.port = port
        self.reset_pin = reset_pin
        self.data_pin = data_pin
        self.onDecode = None

        # set up pigpio connection
        if pi:
            self.pi = pi
        else:
            self.pi = gpio.pi(self.host, self.port)

        self.pi.set_mode(data_pin, gpio.OUTPUT)
        self.pi.set_pull_up_down(data_pin, gpio.PUD_OFF)
        self.pi.write(data_pin, 0)

        if not self.pi.connected:
            self.debug("Could not connected to " + self.host)
            exit()
        self.callback = None


        # initialize timestamp for further use
        self.start_tick = self.pi.get_current_tick()

        # control variables
        self.active = False     # enables the decoder 

        # symbol parameters
        self.pulse_medium_gap_µs = 2650 #µs
        self.pulse_long_gap_µs = 4700 #µs
        self.pulse_verylong_gap_µs = 9600 #µs
        self.symbol_tolerance_µs = 200 #µs

        # decoding variables
        self.state = 0  # 0=idle; 1=frame;
        self.symbols = np.empty(0, dtype=np.uint8)

        # sensor data
        self.sensor_id = 0
        self.temperature = 0
        self.humidity = 0
        self.channel = 0
        self.battery_ok = False
        self.txMode = 0
        self.newData = False

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
            print(message)

    def cbf(self, pin, level, tick):
        # End of Pulse
        if level == 0:
            pass
        # End of Gap
        if level == 1:
            delta = gpio.tickDiff(self.start_tick, tick)
            self.start_tick = tick
            # use frame-gap after 1st frame as trigger to scan the next frames; pulse + very long gap
            if self.state == 0 and delta in range(self.pulse_verylong_gap_µs - self.symbol_tolerance_µs, self.pulse_verylong_gap_µs + self.symbol_tolerance_µs):
                self.debug("Start of frame detected", TRACE)
                self.state = 1
            # pulse + long gap => 1           
            elif (self.state == 1) and delta in range(self.pulse_long_gap_µs - self.symbol_tolerance_µs, self.pulse_long_gap_µs + self.symbol_tolerance_µs):
                self.symbols = np.append(self.symbols, [1])
            # pulse + medium gap => 0
            elif (self.state == 1) and delta in range(self.pulse_medium_gap_µs - self.symbol_tolerance_µs, self.pulse_medium_gap_µs + self.symbol_tolerance_µs):
                self.symbols = np.append(self.symbols, [0])
            elif (self.state == 1) and delta in range(self.pulse_verylong_gap_µs - self.symbol_tolerance_µs, self.pulse_verylong_gap_µs + self.symbol_tolerance_µs):
                self.debug("End of Frame : " + str(self.symbols.size)+ " Bits received", TRACE)
                if self.symbols.size == 37:
                    self.state = 2  # all good
                else:
                    self.symbols = np.empty(0, dtype=np.uint8)
                    self.state = 0
            else:
                pass
        # Watchdog timeout
        elif (level == 2) and (self.state > 0):
            self.debug("End of Transmission: " + str(self.symbols.size) + " Bits received", TRACE)
            if self.symbols.size == 37:
                self.decode()
            else:
                pass
            self.symbols = np.empty(0, dtype=np.uint8)
            self.state = 0
        else:
            pass

    def decode(self):
        """Actual decoder"""
        frame = np.packbits(self.symbols)

        temp_raw = (frame[2] << 4) | (frame[3] >> 4)
        # handle negative numbers
        if temp_raw > 0x7ff:
            temp_raw -= 2**12

        # convert to actual temperature
        self.temperature = float(temp_raw)/10.
        self.humidity = int(((frame[3] & 0x07) << 4) | (frame[4] >> 4))
        self.channel = int(frame[1] & 0x03)
        self.txMode = int(frame[1] & 0x04)
        self.sensor_id = int(((frame[0] & 0x0f) << 4) | (frame[1] >> 4))
        self.newData = True
        self.debug("{} Frame: ".format(datetime.now().isoformat(timespec='seconds')) + ''.join('{:02X} '.format(x) for x in frame) + " - ID={}  Channel={} txMode={}  {:.1f}°C  {:.0f}% rH".format(self.sensor_id, self.channel, self.txMode, self.temperature, self.humidity), INFO)

    def run(self, glitch_filter=150, onDecode=None):
        # callback after successful decode
        self.onDecode=onDecode

        # filter high frequency noise
        self.pi.set_glitch_filter(self.data_pin, glitch_filter)

        # watchdog to detect end of frame
        self.pi.set_watchdog(self.data_pin, 18)    # 18ms=18000µs

        # watch pin
        self.callback = self.pi.callback(self.data_pin, gpio.EITHER_EDGE, self.cbf)

        while 1:
            sleep(60)
            if self.newData:
                # publish values into MQTT topics
                if self.onDecode:
                    self.onDecode("home/greenhouse/temp", '{0:0.1f}'.format(self.temperature))
                    self.onDecode("home/greenhouse/hum", '{0:0.0f}'.format(self.humidity))
                self.newData = False

            
class Mqtt(object):
    def __init__(self, host="localhost", debug_level=SILENT):
        self.debug_level = debug_level
        self.host = host
        self.connected = False

        self.client = mqtt.Client('raspi-%s' % os.getpid())
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
            print(message)

    def publish(self, topic, data, retain=False):
        if self.connected:
            self.client.publish(topic, data, retain)

    def on_connect(self, client, userdata, flags, rc):
        self.debug(("Connected to mqtt broker:", self.host), TRACE)
        self.connected = True


def main():
    """ main function """

    # set up decoder and mqtt-connection
    with Rfm69(host="localhost", channel=0, baudrate=32000) as rf:
        # just to make sure SPI is working
        rx_data = rf.read_single(0x5A)
        if rx_data != 0x55:
            print("SPI Error")
            exit()

        # Configure
        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY
        rf.write_burst(0x07, [0x6C, 0x7A, 0xE1])      # Frf: Carrier Frequency 434MHz        
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz
        rf.write_single(0x1B, 0b01000011)     # ThresType: Peak, Decrement RSSI thresold once every 8 chips (max)
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        # Receive mode
        rf.write_single(0x01, 0b00010000)     # OpMode: SequencerOn, RX

        # wait until RFM-Module is ready
        counter = 0
        while (rf.read_single(0x27) & 0x80) == 0:
            counter = counter + 1
            if counter > 100:
                raise Exception("ERROR - Could not initialize RFM-Module")

        with Decoder(host="localhost", debug_level=INFO) as decoder:
            with Mqtt(host="omv4", debug_level=SILENT) as mqtt_client:
                try:
                    decoder.run(glitch_filter=400, onDecode=mqtt_client.publish)
                except KeyboardInterrupt:
                    print("cancel")

if __name__ == "__main__":
    main()