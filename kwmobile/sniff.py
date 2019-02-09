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
HOST = "rfpi"

start_tick = 0
state = 0 # 0=Idle, 1=Frame
bits = None

def cbf(pin, level, tick):
    global start_tick
    global state
    global bits
    if level == 1:
        start_tick = tick
    elif level == 0:
        delta = gpio.tickDiff(start_tick, tick)
        if (state == 0) and (delta > 5300) and (delta < 5700):
            bits = np.empty(0, dtype=np.uint8)
            state = 1
        elif (state == 1) and (delta < 500):
            bits = np.append(bits, [0])
        elif (state == 1) and (delta > 500) and (delta < 1000):
            bits = np.append(bits, [1])
        elif state == 1:
            # print
            if bits.size >= 32:
                print "Rx: "+''.join('0x{:02X} '.format(x) for x in np.packbits(bits)[:4])
            state = 0
        else:
            pass
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

        rf.write_burst(0x07, [0xD9, 0x12, 0x00])      # Carrier Frequency 868.25MHz

        rf.write_single(0x18, 0b00000000)     # Lna: 50 Ohm, auto gain
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz

        # Receive
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        rf.write_single(0x01, 0b00010000)     # OpMode: SequencerOn, RX

        # wait until RFM-Module is ready
        while (rf.read_single(0x27) & 0x80) == 0:
            print "waiting..."

        # filter high frequency noise
        pi.set_glitch_filter(DATA, 150)

        # watch pin
        callback = pi.callback(DATA, gpio.EITHER_EDGE, cbf)

        print "Scanning... Press Ctrl-C to abort"
        while 1:
            sleep(1)

    pi.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print ""
    finally:
        print "done"
