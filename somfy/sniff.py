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
bits = np.empty(0, dtype=np.uint8)

def cbf(pin, level, tick):
    global start_tick
    global state
    global bits

    # End of Gap
    if level == 1:
        delta = gpio.tickDiff(start_tick, tick)
        start_tick = tick
        # long gap
        if (state == 1) and (delta > 1200) and (delta < 1400):
            bits = np.append(bits, [0, 0])
        # short gap
        elif (state == 1) and (delta > 550) and (delta < 750):
            bits = np.append(bits, [0])
        else:
            pass

    # End of Pulse
    elif level == 0:
        delta = gpio.tickDiff(start_tick, tick)
        start_tick = tick
        # start of frame
        if (state == 0) and (delta > 4600) and (delta < 5000):
            bits = np.empty(0, dtype=np.uint8)
            state = 1
        # long pulse
        elif (state == 1) and (delta > 1200) and (delta < 1400):
            bits = np.append(bits, [1, 1])
        # short pulse
        elif (state == 1) and (delta > 550) and (delta < 750):
            bits = np.append(bits, [1])
        else:
            pass

    # Watchdog timeout
    elif (level == 2) and (state == 1):
        # skip first bit, because it is part of the start of frame mark
        bits = bits[1::]

        # append one zero-bit, in case the last bit was a one and the last zero-bit can't be detected, because the frame is over
        if bits.size < 112:
            bits = np.append(bits, [0])
        if bits.size == 112:
            decoded = np.ravel(np.where(np.reshape(bits, (-1, 2)) == [0, 1], 1, 0))[::2]
            frame = np.packbits(decoded)

            for i in range(frame.size-1, 0, -1):
                frame[i] = frame[i] ^ frame[i-1]

            cksum = frame[0] ^ (frame[0] >> 4)
            for i in range(1,7):
                cksum = cksum ^ frame[i] ^ (frame[i] >> 4)
            cksum = cksum & 0x0f
            
            print "Frame: "+''.join('0x{:02X} '.format(x) for x in frame)
            print "    Control: 0x{:02X}".format((frame[1] >> 4) & 0x0f)
            print "    Checksum: {}".format("ok" if cksum==0 else "error")
            print "    Address: "+''.join('{:02X} '.format(x) for x in frame[4:7])
            print "    Rolling Code: "+''.join('{:02X} '.format(x) for x in frame[2:4])
        else:
            pass
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

        rf.write_burst(0x07, [0x6C, 0x7A, 0x00]) # Frf: Carrier Frequency 434MHz

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

        # watchdog to detect end of frame (20ms)
        pi.set_watchdog(DATA, 20)

        # watch DATA pin
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
