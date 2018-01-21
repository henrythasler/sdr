#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OOK-Decoder"""

from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np
import sys

RESET = 24
DATA = 25

def main(code):
    """ main function """
    pi = gpio.pi(host="rfpi")
    if not pi.connected:
        exit()    
    pi.set_mode(RESET, gpio.OUTPUT) 
    pi.set_mode(DATA, gpio.OUTPUT)
    pi.set_pull_up_down(DATA, gpio.PUD_OFF)
    pi.write(DATA, 0)

    pi.write(RESET, 1)
    pi.write(RESET, 0)

    with Rfm69(host="rfpi", channel=0, baudrate=32000, debug_level=3) as rf:

        # just to make sure SPI is working
        rx_data = rf.read_single(0x5A)
        if rx_data != 0x55:
            print "SPI Error"

        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY
        
#        rf.write_burst(0x07, [0x6C, 0x7A, 0x00]) # Frf: Carrier Frequency 434MHz
        rf.write_burst(0x07, [0xD9, 0x12, 0x00])      # Carrier Frequency 868.25MHz

        # Use PA_BOOST
        rf.write_single(0x13, 0x0F)     
        rf.write_single(0x5A, 0x5D)     
        rf.write_single(0x5C, 0x7C)     
        rf.write_single(0x11, 0b01111111)     # Use PA_BOOST

        rf.write_single(0x18, 0b00000110)     # Lna: 50 Ohm, highest gain
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz

        # Transmit
        rf.write_single(0x02, 0b01101000)     # DataModul: OOK, continuous w/o bit sync
        rf.write_single(0x01, 0b00001100)     # OpMode: SequencerOn, TX

        while (rf.read_single(0x27) & 0x80) == 0:
            pass
            #print "waiting..."

        pi.wave_clear()

        # unique 32-bit code for each unit
        data = np.empty(0, dtype=np.uint8)
        for item in code:
            data = np.append(data, np.array(int(item, 16), dtype=np.uint8))

        # how many consecutive frame repetitions
        repetitions = 5

        # create preamble pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 5430), gpio.pulse(0, 1<<DATA, 334)])
        preamble = pi.wave_create();

        # create "0" pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 334), gpio.pulse(0, 1<<DATA, 666)])
        zero = pi.wave_create();

        # create "1" pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 666), gpio.pulse(0, 1<<DATA, 334)])
        one = pi.wave_create();

        # create bitstream from data
        bits = np.where(np.unpackbits(data) == 1, one, zero)

        # assemble whole frame
        frame = np.concatenate(([255,0], [preamble], bits, [255, 1, repetitions, 0]))

        # send frame
        pi.wave_chain(frame.tolist())

        # wait until finished
        while pi.wave_tx_busy():
            sleep(0.1);

        # clean up
        pi.wave_delete(preamble)
        pi.wave_delete(zero)
        pi.wave_delete(one)

    # reset transmitter
    pi.write(RESET, 1)
    pi.write(RESET, 0)
    sleep(.005)
    pi.stop()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        # just make sure we don't transmit forever
        pi = gpio.pi()
        pi.write(DATA, 0)
        pi.stop()
    finally:
        #print "done"
        pass
