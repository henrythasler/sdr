#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OOK-Decoder"""

from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np
#import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1 import make_axes_locatable

# define pigpio GPIO-pins where RESET- and DATA-Pin of RFM69-Transceiver are connected
RESET = 24
DATA = 25

# define pigpio-host
HOST = "localhost"

start_tick = 0
state = 0 # 0=Idle, 1=Frame
bits = np.empty(0, dtype=np.uint8)
hw_sync = np.empty(0)
tolerance = 100 #µs
clock = 640

histogram = [0, np.zeros(56)]

def cbf(pin, level, tick):
    global start_tick
    global state
    global bits
    global hw_sync
    global clock
    global histogram

    # End of Gap
    if level == 1:
        delta = gpio.tickDiff(start_tick, tick)
        start_tick = tick
        # HW-Sync
        if (0 <= state <=2) and (delta in range(2500-2*tolerance, 2500+2*tolerance)):
            if state < 2:
                hw_sync = np.empty(0)
            hw_sync = np.append(hw_sync, [delta])
            state = 2
        # long gap
        elif (state == 3) and (delta in range(2*clock-tolerance, 2*clock+tolerance)):
            bits = np.append(bits, [0, 0])
        # short gap
        elif (state == 3) and (delta in range(clock-tolerance, clock+tolerance)):
            bits = np.append(bits, [0])
        else:
            pass

    # End of Pulse
    elif level == 0:
        delta = gpio.tickDiff(start_tick, tick)
        start_tick = tick
        # wake-up pulse
        if (state == 0) and (delta in range(10050-tolerance, 10050+tolerance)):
            state = 1
        # HW-Sync
        elif (0 <= state <=2) and (delta in range(2500-2*tolerance, 2500+2*tolerance)):
            if state < 2:
                hw_sync = np.empty(0)
            hw_sync = np.append(hw_sync, [delta])
            state = 2
        # start of frame mark
        elif (state == 2) and (delta in range(4850-2*tolerance, 4850+2*tolerance)):
            clock = int(np.average(hw_sync)/4)
            print("Clock Sync:", hw_sync, clock)
            bits = np.empty(0, dtype=np.uint8)
            state = 3
        # long pulse
        elif (state == 3) and (delta in range(2*clock-tolerance, 2*clock+tolerance)):
            bits = np.append(bits, [1, 1])
        # short pulse
        elif (state == 3) and (delta in range(clock-tolerance, clock+tolerance)):
            bits = np.append(bits, [1])
        else:
            pass

    # Watchdog timeout
    elif (level == 2) and (state > 0):
        # skip first bit, because it is part of the start of frame mark
        bits = bits[1::]

        # append one zero-bit, in case the last bit was a one and the last zero-bit can't be detected, because the frame is over
        if bits.size < 112:
            bits = np.append(bits, [0])
        if bits.size == 112:
            # decode manchester (rising edge = 1, falling edge = 0)
            decoded = np.ravel(np.where(np.reshape(bits, (-1, 2)) == [0, 1], 1, 0))[::2]

            histogram[1] = histogram[1] + decoded
            histogram[0] += 1

            frame = np.packbits(decoded)
            print("Raw: "+''.join('0x{:02X} '.format(x) for x in frame))

            for i in range(frame.size-1, 0, -1):
                frame[i] = frame[i] ^ frame[i-1]

            cksum = frame[0] ^ (frame[0] >> 4)
            for i in range(1,7):
                cksum = cksum ^ frame[i] ^ (frame[i] >> 4)
            cksum = cksum & 0x0f
            
            print("Frame: "+''.join('0x{:02X} '.format(x) for x in frame))
            print("    Control: 0x{:02X}".format((frame[1] >> 4) & 0x0f))
            print("    Checksum: {}".format("ok" if cksum==0 else "error"))
            print("    Address: "+''.join('{:02X} '.format(x) for x in frame[4:7]))
            print("    Rolling Code: "+''.join('{:02X} '.format(x) for x in frame[2:4]))
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
            print("SPI Error")

        # configure
        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY

        rf.write_burst(0x07, [0x6C, 0x9A, 0x00]) # Frf: Carrier Frequency 434.42MHz/61.035 

#        rf.write_single(0x18, 0b00000000)     # Lna: 50 Ohm, auto gain

#        rf.write_single(0x19, 0b01001001)     # RxBw: 4% DCC, BW=100kHz
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz

        # make sure we conserve the thesold setting in between WUP and HW-Sync
        rf.write_single(0x1B, 0b01000011)     # ThresType: Peak, Decrement RSSI thresold once every 8 chips (max)
#        rf.write_single(0x1D, 50)            # OokFix

        # Receive
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        rf.write_single(0x01, 0b00010000)     # OpMode: SequencerOn, RX

        # wait until RFM-Module is ready
        while (rf.read_single(0x27) & 0x80) == 0:
            print("waiting...")

        # filter high frequency noise
        pi.set_glitch_filter(DATA, 150)

        # watchdog to detect end of frame (20ms)
        pi.set_watchdog(DATA, 20)

        # watch DATA pin
        callback = pi.callback(DATA, gpio.EITHER_EDGE, cbf)

        print("Scanning... Press Ctrl-C to abort")
        while 1:
            sleep(1)

    pi.stop()

def show_histogram(matrix, normalize=1):
    fig, ax = plt.subplots()
    matrix = matrix/normalize
    img1 = ax.imshow(matrix)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(img1, cax=cax)
    plt.show()        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
    finally:
        print("done")
#        if histogram[0] > 0:
#            show_histogram(np.reshape(histogram[1], (-1, 8)), normalize=histogram[0])
