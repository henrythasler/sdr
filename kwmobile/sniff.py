#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OOK-Decoder"""

from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np

# define pigpio GPIO-pins where RESET- and DATA-Pin of RFM69-Transceiver are connected
RESET = 24
DATA = 25

# define pigpio-host
HOST = "raspberrypi"

start_tick = 0
state = 0 # 0=Idle, 1=Frame
bits = np.empty(0, dtype=np.uint8)
tolerance = 50 #µs

def cbf(pin, level, tick):
    global start_tick
    global state
    global bits
    global tolerance

    # End of Pulse
    if level == 0:
        pass
    # End of Gap
    if level == 1:
        delta = gpio.tickDiff(start_tick, tick)
        start_tick = tick
        # use frame-gap after 1st frame as trigger to scan the next frames; pulse + very long gap
        if state == 0 and delta in range(4500-4*tolerance, 4500+4*tolerance):
            state = 1
        # pulse + long gap            
        elif (state == 1) and delta in range(2500-2*tolerance, 2500+2*tolerance):
            bits = np.append(bits, [1])
        # pulse + short gap
        elif (state == 1) and delta in range(1500-2*tolerance, 1500+2*tolerance):
            bits = np.append(bits, [0])
        else:
            pass

    # Watchdog timeout
    elif (level == 2) and (state > 0):
        if bits.size == 36:
            frame = np.packbits(bits)
            temperature = ((frame[1]&0x0f) << 8 | frame[2])/10.
            humidity = (((frame[3]&0x0f) << 4) + (frame[4]>>4))
            channel = (frame[1]&0x30) >> 4
            battery = (frame[1]&0x80) == 0x80
            id = frame[0]
            print "Frame: "+''.join('{:02X} '.format(x) for x in frame) + " - ID={}  Channel={} Battery={}  {:.1f}°C  {:.0f}% rH".format(id, channel, battery, temperature, humidity)
        else:
            pass
        bits = np.empty(0, dtype=np.uint8)
        state = 0
    else:
        pass

def main():
    """ main function """
    pi = gpio.pi(host=HOST)
    if not pi.connected:
        exit()
    pi.set_mode(RESET, gpio.OUTPUT)
    pi.set_mode(DATA, gpio.OUTPUT)
    pi.set_pull_up_down(DATA, gpio.PUD_OFF)
    pi.write(DATA, 0)

    pi.write(RESET, 1)
    pi.write(RESET, 0)

    with Rfm69(host=HOST, channel=0, baudrate=32000, debug_level=0) as rf:

        # just to make sure SPI is working
        rx_data = rf.read_single(0x5A)
        if rx_data != 0x55:
            print "SPI Error"

        # configure
        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY

        rf.write_burst(0x07, [0x6C, 0x7A, 0xE1])      # Frf: Carrier Frequency 434MHz        

        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz
        rf.write_single(0x1B, 0b01000011)     # ThresType: Peak, Decrement RSSI thresold once every 8 chips (max)

        # Receive
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        rf.write_single(0x01, 0b00010000)     # OpMode: SequencerOn, RX

        # wait until RFM-Module is ready
        while (rf.read_single(0x27) & 0x80) == 0:
            print "waiting..."

        # filter high frequency noise
        pi.set_glitch_filter(DATA, 150)

        # watchdog to detect end of frame
        pi.set_watchdog(DATA, 3)    # 3ms=3000µs

        # watch pin
        callback = pi.callback(DATA, gpio.EITHER_EDGE, cbf)

        print "Scanning... Press Ctrl-C to abort"
        while 1:
            sleep(60)
            print "sending..."

    callback.cancel()
    pi.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print ""
    finally:
        print "done"
