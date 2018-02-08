#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OOK-Decoder"""

from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# define pigpio GPIO-pins where RESET- and DATA-Pin of RFM69-Transceiver are connected
RESET = 24
DATA = 25

# define pigpio-host
HOST = "rfpi"

start_tick = 0
state = 0 # 0=Idle, 1=Frame
bits = np.empty(0, dtype=np.uint8)
tolerance = 50 #µs

histogram = [0, np.zeros(34)]

def cbf(pin, level, tick):
    global start_tick
    global state
    global bits
    global tolerance
    global histogram

    # End of Gap
    if level == 1:
        start_tick = tick

    # End of Pulse
    elif level == 0:
        delta = gpio.tickDiff(start_tick, tick)
#        start_tick = tick
        # long pulse
        if delta in range(820-2*tolerance, 820+2*tolerance):
            bits = np.append(bits, [1])
            state = 1
        # short pulse
        elif delta in range(300-tolerance, 300+tolerance):
            bits = np.append(bits, [0])
        else:
            pass

    # Watchdog timeout
    elif (level == 2) and (state > 0):
        if bits.size == 34:
            histogram[1] = histogram[1] + bits
            histogram[0] += 1
            frame = np.packbits(bits)
            print "Frame: "+''.join('0x{:02X} '.format(x) for x in frame)
            #print "Command: 0b{:08b}".format(((frame[2]&0x0f) << 4) + (frame[3]&0x0f))

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
    pi.set_pull_up_down(DATA, gpio.PUD_DOWN)
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

        rf.write_burst(0x07, [0x6C, 0x9A, 0x00]) # Frf: Carrier Frequency 434.42MHz/61.035 

#        rf.write_single(0x18, 0b00000000)     # Lna: 50 Ohm, auto gain

#        rf.write_single(0x19, 0b01001001)     # RxBw: 4% DCC, BW=100kHz
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz

        # make sure we conserve the thesold setting in between WUP and HW-Sync
        rf.write_single(0x1B, 0b01000011)     # ThresType: Peak, Decrement RSSI thresold once every 8 chips (max)

        # Receive
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        rf.write_single(0x01, 0b00010000)     # OpMode: SequencerOn, RX

        # wait until RFM-Module is ready
        while (rf.read_single(0x27) & 0x80) == 0:
            print "waiting..."

        # filter high frequency noise
        pi.set_glitch_filter(DATA, 150)

        # watchdog to detect end of frame (20ms)
        pi.set_watchdog(DATA, 8)

        # watch DATA pin
        callback = pi.callback(DATA, gpio.EITHER_EDGE, cbf)

        print "Scanning... Press Ctrl-C to abort"
        try:
            while 1:
                sleep(1)
        except KeyboardInterrupt:
            print ""
        finally:
            print "done"
        

    pi.stop()

def show_histogram(matrix, normalize=False):
    fig, ax = plt.subplots()
    if normalize:
        matrix = matrix/np.amax(matrix)
    #print matrix.size, matrix
    img1 = ax.imshow(matrix)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(img1, cax=cax)
    plt.show()        

if __name__ == "__main__":
    main()      

    if histogram[0] > 0:
        show_histogram(np.reshape(np.append(histogram[1], np.zeros(6)), (-1, 8)), normalize=True)
